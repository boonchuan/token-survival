"""
Shared configuration, database connection, and logging.
Loads from env vars; defaults are dev placeholders.
"""
import os
import logging
import logging.handlers
from pathlib import Path
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Database
DB_HOST = os.getenv("TS_DB_HOST", "localhost")
DB_PORT = int(os.getenv("TS_DB_PORT", "5432"))
DB_NAME = os.getenv("TS_DB_NAME", "token_survival")
DB_USER = os.getenv("TS_DB_USER", "delta-dev")
DB_PASS = os.getenv("TS_DB_PASS", "")

# Sample frame
START_DATE = "2014-01-01"
END_DATE = "2024-12-31"
SNAPSHOT_FREQUENCY_DAYS = 30  # ~monthly cadence

# HTTP politeness
HTTP_TIMEOUT = 30
HTTP_USER_AGENT = "TokenSurvivalResearch/0.1 (academic; contact: independent researcher SG)"
WAYBACK_RATE_LIMIT_SEC = 2.0    # Wayback asks for slow scraping
CMC_API_RATE_LIMIT_SEC = 1.0
CG_API_RATE_LIMIT_SEC = 1.5

# Death definitions
DEATH_DEFINITIONS = {
    "primary":    {"window_days": 180, "vol_max": 1000.0,  "ath_ratio_max": 0.01, "require_top_n": 2000, "use_volume": True,  "use_rank": True},
    "loose":      {"window_days": 90,  "vol_max": 1000.0,  "ath_ratio_max": 0.01, "require_top_n": 2000, "use_volume": True,  "use_rank": True},
    "strict":     {"window_days": 365, "vol_max": 1000.0,  "ath_ratio_max": 0.01, "require_top_n": 2000, "use_volume": True,  "use_rank": True},
    "price_only": {"window_days": 180, "vol_max": None,    "ath_ratio_max": 0.01, "require_top_n": None, "use_volume": False, "use_rank": False},
}


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")

    fh = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{name}.log", maxBytes=10_000_000, backupCount=5
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger


@contextmanager
def get_conn():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS,
    )
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor(commit: bool = True, dict_cursor: bool = False):
    with get_conn() as conn:
        cursor_factory = RealDictCursor if dict_cursor else None
        cur = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cur
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()


def cohort_half_label(date_str: str) -> str:
    """'2018-03-15' -> '2018H1'"""
    year = int(date_str[:4])
    month = int(date_str[5:7])
    half = "H1" if month <= 6 else "H2"
    return f"{year}{half}"


__all__ = [
    "PROJECT_ROOT", "DATA_DIR", "LOG_DIR",
    "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASS",
    "START_DATE", "END_DATE", "SNAPSHOT_FREQUENCY_DAYS",
    "HTTP_TIMEOUT", "HTTP_USER_AGENT",
    "WAYBACK_RATE_LIMIT_SEC", "CMC_API_RATE_LIMIT_SEC", "CG_API_RATE_LIMIT_SEC",
    "DEATH_DEFINITIONS",
    "get_logger", "get_conn", "get_cursor", "execute_values",
    "cohort_half_label",
]
