"""
Compute deaths under the Feder et al. (2018) / Schmitz & Hoffmann (2020) definition
for a direct comparison with our primary definition.

Feder simplified definition: a coin is dead at month m if its average daily
trading volume during m is <= 1% of the all-time peak monthly volume.
We approximate "monthly volume" with our snapshot 24h volume (closest available).

This produces a single new variant 'feder_simple' alongside the four existing.
"""
import datetime as dt
from collections import defaultdict

from config import END_DATE, get_logger, get_cursor, execute_values

log = get_logger("feder_compare")
VARIANT = "feder_simple"


def _load_panel():
    with get_cursor(dict_cursor=True) as cur:
        cur.execute("""
            SELECT tp.token_id, tp.obs_date, tp.volume_24h_usd,
                   t.first_seen
            FROM token_panel tp
            JOIN tokens t USING (token_id)
            ORDER BY tp.token_id, tp.obs_date
        """)
        rows = cur.fetchall()
    by_token = defaultdict(list)
    for r in rows:
        by_token[r["token_id"]].append(r)
    return by_token


def _death_under_feder(token_obs):
    """
    Feder simplified: dead if avg daily volume in a 30-day window <= 1% of
    peak observed volume to date. We use our snapshot volume as the unit.

    A token is dead at obs_date d if:
      - peak_volume_to_date is non-null and > 0
      - volume at d <= 1% * peak_volume_to_date
    Resurrection (volume back to >=10% of peak) resets the dead flag, per Feder.
    Final classification: dead if dead at last observation and not subsequently
    resurrected. We adopt the same Path B (disappearance) rule as our primary
    definition for consistency.
    """
    if not token_obs:
        return (None, None, None)

    first_seen = token_obs[0]["first_seen"]
    end_date = dt.date.fromisoformat(END_DATE)
    last_obs_date = token_obs[-1]["obs_date"]

    peak_vol = 0.0
    is_currently_dead = False
    death_date = None

    for obs in token_obs:
        v = obs.get("volume_24h_usd") or 0.0
        v = float(v)
        if v > peak_vol:
            peak_vol = v

        if peak_vol <= 0:
            continue

        ratio = v / peak_vol if peak_vol > 0 else 1.0
        if not is_currently_dead and ratio <= 0.01:
            is_currently_dead = True
            death_date = obs["obs_date"]
        elif is_currently_dead and ratio >= 0.10:
            # Resurrection per Feder
            is_currently_dead = False
            death_date = None

    if is_currently_dead and death_date is not None:
        age_days = (death_date - first_seen).days
        return (death_date, age_days, None)

    # Path B: disappeared from CMC, treat as dead at last_obs + 90 days
    days_since_last_obs = (end_date - last_obs_date).days
    if days_since_last_obs >= 90:
        d = min(last_obs_date + dt.timedelta(days=90), end_date)
        age_days = (d - first_seen).days
        return (d, age_days, None)

    age_at_censor = (end_date - first_seen).days
    return (None, None, age_at_censor)


def run():
    panel = _load_panel()
    log.info(f"Loaded panel for {len(panel)} tokens")

    payload = []
    n_dead = 0
    for token_id, obs_list in panel.items():
        death_date, age_at_death, age_at_censor = _death_under_feder(obs_list)
        is_dead = death_date is not None
        if is_dead:
            n_dead += 1
        payload.append((token_id, VARIANT, death_date, is_dead,
                        age_at_death, age_at_censor))

    with get_cursor() as cur:
        cur.execute("DELETE FROM deaths WHERE definition_variant=%s", (VARIANT,))
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
    log.info(f"variant={VARIANT}: {n_dead}/{len(payload)} dead "
             f"({100.0 * n_dead / max(1, len(payload)):.1f}%)")


if __name__ == "__main__":
    run()
