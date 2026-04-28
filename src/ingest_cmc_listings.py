"""
Ingest CSVs produced by fetch_cmc_listings.R into cmc_snapshots.

Each CSV represents one snapshot_date with columns from crypto2::crypto_listings.
We map them to our schema and bulk-insert with conflict handling.

crypto2 columns include (at least):
  id, slug, name, symbol, ref_cur_id, ref_cur_name, snapshot_date,
  open, high, low, close, volume, market_cap, time_open, time_close,
  ... plus other fields when quote=TRUE

We use:
  id        -> cmc_id (the unique CMC identifier)
  symbol    -> symbol
  name      -> name
  market_cap -> market_cap_usd
  close     -> price_usd  (closing price for that snapshot day)
  volume    -> volume_24h_usd
  rank: not provided directly; we derive from market_cap order within snapshot
"""
import csv
import json
import sys
from pathlib import Path

import pandas as pd

from config import DATA_DIR, get_logger, get_cursor, execute_values

log = get_logger("ingest_cmc_listings")

RAW_DIR = DATA_DIR / "raw"


def _ingest_one(csv_path: Path) -> int:
    """Ingest a single per-date CSV. Returns rows inserted."""
    try:
        df = pd.read_csv(csv_path, low_memory=False)
    except Exception as e:
        log.warning(f"Failed to read {csv_path.name}: {e}")
        return 0

    if df.empty:
        log.warning(f"Empty CSV: {csv_path.name}")
        return 0

    # Snapshot date: filename or column
    snap_col = next((c for c in df.columns if c.lower() == "snapshot_date"), None)
    if snap_col:
        df["snapshot_date"] = pd.to_datetime(df[snap_col]).dt.date
    else:
        # Fallback: parse from filename listings_YYYYMMDD.csv
        stem = csv_path.stem
        date_str = stem.replace("listings_", "")
        df["snapshot_date"] = pd.to_datetime(date_str, format="%Y%m%d").date()

    # Tolerate column-name variations
    def col(*names):
        for n in names:
            for c in df.columns:
                if c.lower() == n.lower():
                    return c
        return None

    c_id     = col("id", "cmc_id")
    c_sym    = col("symbol")
    c_name   = col("name")
    c_mcap   = col("market_cap", "marketcap", "market_cap_usd")
    c_close  = col("close", "price", "price_usd")
    c_vol    = col("volume24h", "volume", "volume_24h", "volume_24h_usd")
    c_supply = col("circulating_supply", "supply")
    c_rank   = col("cmc_rank", "rank")

    if c_sym is None:
        log.error(f"{csv_path.name}: no symbol column found. cols={list(df.columns)[:20]}")
        return 0

    # Use crypto2's authoritative cmc_rank if present; else derive from market cap
    if c_rank and c_rank in df.columns:
        df["rank"] = pd.to_numeric(df[c_rank], errors="coerce")
    elif c_mcap and c_mcap in df.columns:
        df = df.sort_values(c_mcap, ascending=False, na_position="last").reset_index(drop=True)
        df["rank"] = df.index + 1
    else:
        df["rank"] = None

    # Build payload
    payload = []
    for _, row in df.iterrows():
        sym = str(row[c_sym]).upper().strip() if c_sym else None
        if not sym or sym == "NAN":
            continue
        snap_date = row["snapshot_date"]
        cmc_id = str(int(row[c_id])) if c_id and pd.notna(row[c_id]) else None
        name = row[c_name] if c_name and pd.notna(row[c_name]) else None
        mcap = float(row[c_mcap]) if c_mcap and pd.notna(row[c_mcap]) else None
        price = float(row[c_close]) if c_close and pd.notna(row[c_close]) else None
        vol = float(row[c_vol]) if c_vol and pd.notna(row[c_vol]) else None
        supply = float(row[c_supply]) if c_supply and pd.notna(row[c_supply]) else None
        rank_v = int(row["rank"]) if pd.notna(row["rank"]) else None

        # Stash everything else as raw_json for forensics
        raw = {k: (None if pd.isna(v) else v) for k, v in row.items()}
        # JSON serialize: convert numpy types
        raw_serializable = {}
        for k, v in raw.items():
            if hasattr(v, "item"):
                v = v.item()
            elif hasattr(v, "isoformat"):
                v = v.isoformat()
            raw_serializable[str(k)] = v

        payload.append((
            snap_date, "crypto2", str(csv_path.name), rank_v, sym, name, cmc_id,
            mcap, price, vol, supply, json.dumps(raw_serializable, default=str),
        ))

    if not payload:
        return 0

    with get_cursor() as cur:
        # The schema uses two partial unique indexes to avoid dropping
        # legitimately distinct tokens that share a symbol on the same date.
        # ON CONFLICT against partial indexes requires repeating the WHERE clause.
        # Since cmc_id is always present from crypto2 output, we hit the cmc_id index.
        execute_values(
            cur,
            """
            INSERT INTO cmc_snapshots
                (snapshot_date, source, source_url, rank, symbol, name, cmc_id,
                 market_cap_usd, price_usd, volume_24h_usd, circulating_supply, raw_json)
            VALUES %s
            ON CONFLICT (snapshot_date, cmc_id, source) WHERE cmc_id IS NOT NULL
            DO NOTHING
            """,
            payload,
            page_size=2000,
        )

    return len(payload)


def run():
    if not RAW_DIR.exists():
        log.error(f"No raw directory: {RAW_DIR}")
        sys.exit(1)

    csv_files = sorted(RAW_DIR.glob("listings_*.csv"))
    if not csv_files:
        log.warning(f"No CSV files in {RAW_DIR}")
        return

    log.info(f"Ingesting {len(csv_files)} CSVs from {RAW_DIR}")
    total = 0
    for csv_path in csv_files:
        n = _ingest_one(csv_path)
        log.info(f"  {csv_path.name}: {n} rows")
        total += n
    log.info(f"DONE: {total} total rows inserted across {len(csv_files)} files")


if __name__ == "__main__":
    run()
