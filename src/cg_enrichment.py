"""
CoinGecko API enrichment.

Pulls chain (asset platform) and category tags for every token in our `tokens`
table that we can match by symbol or by name. CG's free API allows ~30 calls/min;
we cache aggressively.

Workflow:
1. Fetch CG /coins/list once -> id, symbol, name mapping
2. For each token in our DB, find best CG match (symbol + name fuzzy match)
3. Fetch /coins/{id} to get platforms (chain) and categories
4. Map CG categories to our coarse buckets (L1/DeFi/meme/infra/gaming/stablecoin/other)

Run AFTER tokens table has been populated by build_panel.py.
"""
import time
import json
from typing import Optional

import requests

from config import (
    HTTP_TIMEOUT, HTTP_USER_AGENT, CG_API_RATE_LIMIT_SEC,
    DATA_DIR, get_logger, get_cursor,
)

log = get_logger("cg_enrichment")

CG_BASE = "https://api.coingecko.com/api/v3"
COINS_LIST_CACHE = DATA_DIR / "cg_coins_list.json"
COIN_DETAIL_CACHE_DIR = DATA_DIR / "cg_coin_details"
COIN_DETAIL_CACHE_DIR.mkdir(exist_ok=True)

# Coarse category mapping. CG categories are finer-grained than we want.
# Order matters: first match wins.
CATEGORY_RULES = [
    ("stablecoin",  ["stablecoin", "usd-stablecoin", "eur-stablecoin"]),
    ("meme",        ["meme", "memes", "dog-themed", "cat-themed", "frog-themed"]),
    ("DeFi",        ["decentralized-finance-defi", "defi", "yield", "lending", "dex",
                     "decentralized-exchange", "yield-farming", "liquid-staking"]),
    ("gaming",      ["gaming", "play-to-earn", "metaverse", "nft", "non-fungible-tokens",
                     "gamefi", "collectibles-nfts"]),
    ("infra",       ["oracle", "storage", "interoperability", "cross-chain",
                     "data-availability", "infrastructure", "rollup", "zero-knowledge",
                     "modular-blockchain"]),
    ("L1",          ["smart-contract-platform", "layer-1", "proof-of-work",
                     "proof-of-stake", "layer-2"]),
]

# Asset platform id -> our chain bucket
PLATFORM_TO_CHAIN = {
    "ethereum": "ETH",
    "binance-smart-chain": "BSC",
    "binancecoin": "BSC",
    "solana": "SOL",
    "tron": "TRX",
    "polygon-pos": "ETH",   # treat L2/sidechains as ETH-family
    "arbitrum-one": "ETH",
    "optimistic-ethereum": "ETH",
    "base": "ETH",
    "avalanche": "other",
    "fantom": "other",
}


def _get(url: str, params: Optional[dict] = None) -> Optional[dict]:
    try:
        time.sleep(CG_API_RATE_LIMIT_SEC)
        r = requests.get(url, params=params,
                         headers={"User-Agent": HTTP_USER_AGENT},
                         timeout=HTTP_TIMEOUT)
        if r.status_code == 429:
            log.warning("CG rate-limited; sleeping 60s")
            time.sleep(60)
            r = requests.get(url, params=params,
                             headers={"User-Agent": HTTP_USER_AGENT},
                             timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning(f"CG GET failed {url}: {e}")
        return None


def fetch_coins_list(force: bool = False) -> list[dict]:
    """One-time fetch of CG's full coin list (~12k entries)."""
    if COINS_LIST_CACHE.exists() and not force:
        return json.loads(COINS_LIST_CACHE.read_text())
    data = _get(f"{CG_BASE}/coins/list", {"include_platform": "true"})
    if data:
        COINS_LIST_CACHE.write_text(json.dumps(data))
        log.info(f"Cached {len(data)} CG coins")
    return data or []


def _build_match_index(coins_list: list[dict]) -> dict[str, list[dict]]:
    """symbol_upper -> list of CG coin dicts that share that symbol."""
    idx = {}
    for c in coins_list:
        sym = c.get("symbol", "").upper()
        if sym:
            idx.setdefault(sym, []).append(c)
    return idx


def _best_cg_match(symbol: str, name: str, idx: dict) -> Optional[dict]:
    candidates = idx.get(symbol.upper(), [])
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # Multiple symbol collisions; prefer exact name match
    name_lower = (name or "").lower().strip()
    for c in candidates:
        if c.get("name", "").lower().strip() == name_lower:
            return c
    # Otherwise prefer one with most platforms (suggests it's the more established token)
    return max(candidates, key=lambda c: len(c.get("platforms") or {}))


def fetch_coin_detail(cg_id: str) -> Optional[dict]:
    cache_path = COIN_DETAIL_CACHE_DIR / f"{cg_id}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())
    data = _get(f"{CG_BASE}/coins/{cg_id}", {
        "localization": "false", "tickers": "false",
        "market_data": "false", "community_data": "false",
        "developer_data": "false",
    })
    if data:
        cache_path.write_text(json.dumps(data))
    return data


def _classify_chain(platforms: dict) -> str:
    """Pick the dominant chain from platforms dict."""
    if not platforms:
        return "native"
    for platform_id in platforms.keys():
        if platform_id in PLATFORM_TO_CHAIN:
            return PLATFORM_TO_CHAIN[platform_id]
    return "other"


def _classify_category(categories: list[str]) -> str:
    if not categories:
        return "other"
    cats_lower = [c.lower().replace(" ", "-") for c in categories if c]
    for bucket, keywords in CATEGORY_RULES:
        for kw in keywords:
            if any(kw in c for c in cats_lower):
                return bucket
    return "other"


def enrich_all_tokens():
    """Update tokens table with chain and category."""
    coins_list = fetch_coins_list()
    idx = _build_match_index(coins_list)

    with get_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT token_id, symbol, name FROM tokens "
                    "WHERE chain IS NULL OR category IS NULL")
        rows = cur.fetchall()

    log.info(f"Enriching {len(rows)} tokens")
    n_matched = 0
    n_unmatched = 0

    for row in rows:
        match = _best_cg_match(row["symbol"], row["name"], idx)
        if match is None:
            n_unmatched += 1
            with get_cursor() as cur:
                cur.execute(
                    "UPDATE tokens SET chain=COALESCE(chain,'unknown'), "
                    "category=COALESCE(category,'other') WHERE token_id=%s",
                    (row["token_id"],),
                )
            continue

        detail = fetch_coin_detail(match["id"])
        if detail is None:
            continue

        chain = _classify_chain(detail.get("platforms") or match.get("platforms") or {})
        category = _classify_category(detail.get("categories") or [])

        with get_cursor() as cur:
            cur.execute(
                "UPDATE tokens SET chain=%s, category=%s, cmc_id=COALESCE(cmc_id,%s) "
                "WHERE token_id=%s",
                (chain, category, match["id"], row["token_id"]),
            )
        n_matched += 1

        if n_matched % 100 == 0:
            log.info(f"  enriched {n_matched}/{len(rows)}")

    log.info(f"Done. matched={n_matched}, unmatched={n_unmatched}")


if __name__ == "__main__":
    enrich_all_tokens()
