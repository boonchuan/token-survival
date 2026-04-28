"""
Build canonical tokens registry and token_panel from raw cmc_snapshots.

Steps:
1. Resolve symbol collisions: symbols that map to >1 distinct cmc_id (or distinct
   names with no overlap in time) are split into separate token_ids.
2. For each token, compute first_seen, last_seen, initial market cap/volume/rank,
   peak price, peak_mcap, cohort_half.
3. Populate token_panel: one row per (token_id, snapshot_date) with rank, mcap,
   price, volume, drawdown_from_ath, in_top_2000.

Idempotent: re-running drops and rebuilds tokens / token_panel from current
cmc_snapshots. Run after each scrape pass.
"""
import datetime as dt
from collections import defaultdict

from config import get_logger, get_cursor, execute_values, cohort_half_label

log = get_logger("build_panel")


def _wipe_derived_tables():
    with get_cursor() as cur:
        cur.execute("TRUNCATE token_panel CASCADE")
        cur.execute("TRUNCATE tokens RESTART IDENTITY CASCADE")
    log.info("Wiped tokens and token_panel")


def _load_snapshots():
    """Pull all snapshot rows. For our scale (~25k tokens x 130 snapshots = 3M rows max)
    this is fine to hold in memory."""
    with get_cursor(dict_cursor=True) as cur:
        cur.execute("""
            SELECT snapshot_date, symbol, name, cmc_id, rank, market_cap_usd,
                   price_usd, volume_24h_usd
            FROM cmc_snapshots
            ORDER BY snapshot_date, rank NULLS LAST
        """)
        return cur.fetchall()


def _resolve_token_keys(snapshot_rows):
    """
    Return: dict[(symbol, resolution_key)] -> list of snapshot rows.
    resolution_key is cmc_id when available, else name (normalized), else just symbol.

    This handles the case where the same symbol (e.g. 'LUNA') refers to multiple
    distinct tokens at different times.
    """
    grouped = defaultdict(list)
    for r in snapshot_rows:
        sym = r["symbol"].upper().strip()
        if r.get("cmc_id"):
            key = (sym, f"cmc:{r['cmc_id']}")
        elif r.get("name"):
            key = (sym, f"name:{r['name'].lower().strip()}")
        else:
            key = (sym, "_")
        grouped[key].append(r)
    return grouped


def _summarize_token(rows):
    """Compute the time-invariant fields for a single token from its observation rows."""
    rows_sorted = sorted(rows, key=lambda r: r["snapshot_date"])
    first = rows_sorted[0]
    last = rows_sorted[-1]

    # Initial = first snapshot in our data; this is an approximation of "launch"
    initial_mcap = first.get("market_cap_usd")
    initial_vol = first.get("volume_24h_usd")
    initial_rank = first.get("rank")

    # Peak
    peak_price = None
    peak_price_date = None
    peak_mcap = None
    for r in rows_sorted:
        p = r.get("price_usd")
        if p is not None and (peak_price is None or p > peak_price):
            peak_price = p
            peak_price_date = r["snapshot_date"]
        m = r.get("market_cap_usd")
        if m is not None and (peak_mcap is None or m > peak_mcap):
            peak_mcap = m

    return {
        "symbol":   first["symbol"],
        "name":     first.get("name"),
        "cmc_id":   first.get("cmc_id"),
        "first_seen": first["snapshot_date"],
        "last_seen":  last["snapshot_date"],
        "initial_mcap_usd":   initial_mcap,
        "initial_volume_usd": initial_vol,
        "initial_rank":       initial_rank,
        "peak_price_usd":     peak_price,
        "peak_price_date":    peak_price_date,
        "peak_mcap_usd":      peak_mcap,
        "cohort_half":        cohort_half_label(first["snapshot_date"].isoformat()),
    }


def build():
    _wipe_derived_tables()

    rows = _load_snapshots()
    if not rows:
        log.warning("No snapshots in DB. Run wayback_scraper first.")
        return

    log.info(f"Loaded {len(rows)} snapshot rows")
    grouped = _resolve_token_keys(rows)
    log.info(f"Resolved into {len(grouped)} distinct tokens")

    # Insert tokens; collect generated token_ids
    tokens_payload = []
    keys_in_order = list(grouped.keys())
    for k in keys_in_order:
        s = _summarize_token(grouped[k])
        tokens_payload.append((
            s["symbol"], s["name"], s["cmc_id"],
            s["first_seen"], s["last_seen"],
            None, None, None,                # chain, category, ico_flag (filled by enrichment)
            s["initial_mcap_usd"], s["initial_volume_usd"], s["initial_rank"],
            s["peak_price_usd"], s["peak_price_date"], s["peak_mcap_usd"],
            s["cohort_half"],
        ))

    with get_cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO tokens
                (symbol, name, cmc_id, first_seen, last_seen,
                 chain, category, ico_flag,
                 initial_mcap_usd, initial_volume_usd, initial_rank,
                 peak_price_usd, peak_price_date, peak_mcap_usd, cohort_half)
            VALUES %s
            RETURNING token_id, symbol, cmc_id, name
            """,
            tokens_payload,
        )
        returned = cur.fetchall()

    # Map (symbol, cmc_id_or_name) back to token_id
    # Returned order matches insert order, so align with keys_in_order
    key_to_id = {}
    for k, row in zip(keys_in_order, returned):
        key_to_id[k] = row[0]

    log.info(f"Inserted {len(key_to_id)} tokens")

    # Build token_panel rows
    panel_payload = []
    for k, snap_rows in grouped.items():
        token_id = key_to_id[k]
        # Compute running ATH for drawdown
        running_ath = None
        for r in sorted(snap_rows, key=lambda x: x["snapshot_date"]):
            price = r.get("price_usd")
            if price is not None:
                running_ath = price if running_ath is None else max(running_ath, price)
            drawdown = None
            if running_ath and price is not None and running_ath > 0:
                drawdown = (price - running_ath) / running_ath
            in_top_2000 = (r.get("rank") is not None and r["rank"] <= 2000)
            panel_payload.append((
                token_id, r["snapshot_date"],
                r.get("market_cap_usd"), r.get("price_usd"), r.get("volume_24h_usd"),
                r.get("rank"), in_top_2000, drawdown,
            ))

    log.info(f"Inserting {len(panel_payload)} panel rows")
    with get_cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO token_panel
                (token_id, obs_date, market_cap_usd, price_usd, volume_24h_usd,
                 rank, in_top_2000, drawdown_from_ath)
            VALUES %s
            ON CONFLICT (token_id, obs_date) DO NOTHING
            """,
            panel_payload,
            page_size=5000,
        )

    log.info("Panel build complete")


if __name__ == "__main__":
    build()
