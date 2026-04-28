"""
Compute death events under all definition variants in DEATH_DEFINITIONS.

For each token and each variant, find the earliest obs_date such that all
relevant conditions hold continuously for the variant's window_days. If no
such date exists by END_DATE, the token is right-censored.

Key definition mechanics:
- We iterate over the token's panel observations (sparse, ~monthly).
- A token is "in death state at obs_date" if at that obs_date:
    * price_usd / peak_price <= ath_ratio_max (always)
    * volume_24h_usd <= vol_max          (if use_volume)
    * rank > require_top_n OR rank IS NULL (if use_rank)
- We declare death at the first date d such that the token has been
  continuously "in death state" for >= window_days.
- "Continuously" is approximated: every consecutive observation between
  d - window_days and d must satisfy the conditions, AND there must be at
  least 2 such observations (to avoid declaring death on isolated bad readings).

This is deliberately conservative: a token that briefly recovers liquidity
above $1000 will reset the clock.
"""
import datetime as dt
from collections import defaultdict

from config import (
    DEATH_DEFINITIONS, END_DATE, get_logger, get_cursor, execute_values,
)

log = get_logger("compute_deaths")


def _load_panel():
    with get_cursor(dict_cursor=True) as cur:
        cur.execute("""
            SELECT tp.token_id, tp.obs_date, tp.market_cap_usd, tp.price_usd,
                   tp.volume_24h_usd, tp.rank, tp.in_top_2000, tp.drawdown_from_ath,
                   t.first_seen, t.peak_price_usd
            FROM token_panel tp
            JOIN tokens t USING (token_id)
            ORDER BY tp.token_id, tp.obs_date
        """)
        rows = cur.fetchall()
    by_token = defaultdict(list)
    for r in rows:
        by_token[r["token_id"]].append(r)
    return by_token


def _is_in_death_state(obs, peak_price, params):
    """Check the per-observation death conditions."""
    price = obs.get("price_usd")
    peak = peak_price
    if price is None or peak is None or peak <= 0:
        # Missing price: treat as in death state (no liquidity)
        price_dead = True
    else:
        price_dead = (price / peak) <= params["ath_ratio_max"]
    if not price_dead:
        return False

    if params["use_volume"]:
        vol = obs.get("volume_24h_usd")
        # Missing volume on a snapshot we still have = treat as zero (delisted)
        vol_dead = (vol is None) or (vol <= params["vol_max"])
        if not vol_dead:
            return False

    if params["use_rank"]:
        rank = obs.get("rank")
        rank_dead = (rank is None) or (rank > params["require_top_n"])
        if not rank_dead:
            return False

    return True


def _death_date_for_token(token_obs: list, peak_price, params) -> tuple:
    """
    Walk through token observations chronologically. Track the start of the
    current "in death state" run. Declare death at the first obs_date where
    that run has lasted >= window_days AND contains >= 2 observations.

    Returns (death_date, age_at_death_days, age_at_censor_days).
    death_date is None if right-censored.
    """
    if not token_obs:
        return (None, None, None)

    first_seen = token_obs[0]["first_seen"]
    end_date = dt.date.fromisoformat(END_DATE)

    run_start = None     # date the current dead-run began
    run_obs_count = 0    # observations within the current run

    for obs in token_obs:
        if _is_in_death_state(obs, peak_price, params):
            if run_start is None:
                run_start = obs["obs_date"]
                run_obs_count = 1
            else:
                run_obs_count += 1
            run_length_days = (obs["obs_date"] - run_start).days
            if run_length_days >= params["window_days"] and run_obs_count >= 2:
                age_days = (obs["obs_date"] - first_seen).days
                return (obs["obs_date"], age_days, None)
        else:
            run_start = None
            run_obs_count = 0

    # Right-censored
    age_at_censor = (end_date - first_seen).days
    return (None, None, age_at_censor)


def compute_for_variant(panel_by_token, variant_name, params):
    log.info(f"Computing deaths for variant '{variant_name}': {params}")
    payload = []
    n_dead = 0
    for token_id, obs_list in panel_by_token.items():
        peak_price = obs_list[0]["peak_price_usd"]
        death_date, age_at_death, age_at_censor = _death_date_for_token(
            obs_list, peak_price, params
        )
        is_dead = death_date is not None
        if is_dead:
            n_dead += 1
        payload.append((
            token_id, variant_name, death_date, is_dead,
            age_at_death, age_at_censor,
        ))
    with get_cursor() as cur:
        cur.execute("DELETE FROM deaths WHERE definition_variant=%s", (variant_name,))
        execute_values(
            cur,
            """
            INSERT INTO deaths
                (token_id, definition_variant, death_date, is_dead,
                 age_at_death_days, age_at_censor_days)
            VALUES %s
            """,
            payload,
            page_size=5000,
        )
    log.info(f"  variant={variant_name}: {n_dead}/{len(payload)} dead "
             f"({100.0 * n_dead / max(1, len(payload)):.1f}%)")


def run():
    panel = _load_panel()
    log.info(f"Loaded panel for {len(panel)} tokens")
    for variant_name, params in DEATH_DEFINITIONS.items():
        compute_for_variant(panel, variant_name, params)
    log.info("All variants computed")


if __name__ == "__main__":
    run()
