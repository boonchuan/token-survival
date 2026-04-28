-- Token Survival Analysis Database Schema
-- Database: token_survival
-- Created: 2026-04-28

-- Drop in reverse dependency order (dev convenience; remove for prod)
DROP TABLE IF EXISTS deaths CASCADE;
DROP TABLE IF EXISTS token_panel CASCADE;
DROP TABLE IF EXISTS tokens CASCADE;
DROP TABLE IF EXISTS cmc_snapshots CASCADE;
DROP TABLE IF EXISTS scrape_log CASCADE;

-- Raw scraped snapshots from Wayback Machine / CMC API
-- One row per (snapshot_date, rank) pair
CREATE TABLE cmc_snapshots (
    id              BIGSERIAL PRIMARY KEY,
    snapshot_date   DATE NOT NULL,
    source          TEXT NOT NULL,              -- 'wayback', 'cmc_api', 'cg_api'
    source_url      TEXT,
    rank            INTEGER,
    symbol          TEXT NOT NULL,
    name            TEXT,
    cmc_id          TEXT,                       -- CMC slug or numeric id when available
    market_cap_usd  NUMERIC,
    price_usd       NUMERIC,
    volume_24h_usd  NUMERIC,
    circulating_supply NUMERIC,
    raw_json        JSONB,
    inserted_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cmc_snapshots_date ON cmc_snapshots(snapshot_date);
CREATE INDEX idx_cmc_snapshots_symbol ON cmc_snapshots(symbol);
CREATE INDEX idx_cmc_snapshots_cmc_id ON cmc_snapshots(cmc_id);
-- Uniqueness is on cmc_id when present (CMC's authoritative ID), falling back
-- to symbol for legacy Wayback rows where cmc_id is NULL. This prevents the
-- ON CONFLICT clause from dropping legitimately distinct tokens that happen
-- to share a ticker symbol on the same date (very common post-2020).
CREATE UNIQUE INDEX uq_cmc_snapshots_id   ON cmc_snapshots(snapshot_date, cmc_id, source) WHERE cmc_id IS NOT NULL;
CREATE UNIQUE INDEX uq_cmc_snapshots_sym  ON cmc_snapshots(snapshot_date, symbol, source) WHERE cmc_id IS NULL;

-- Canonical token registry: one row per token
-- token_id is our internal identifier; we resolve symbol collisions via cmc_id when possible
CREATE TABLE tokens (
    token_id        BIGSERIAL PRIMARY KEY,
    symbol          TEXT NOT NULL,
    name            TEXT,
    cmc_id          TEXT UNIQUE,
    first_seen      DATE NOT NULL,
    last_seen       DATE NOT NULL,
    chain           TEXT,                       -- 'ETH','BSC','SOL','TRX','native','other'
    category        TEXT,                       -- 'L1','DeFi','meme','infra','gaming','stablecoin','other'
    ico_flag        BOOLEAN,
    initial_mcap_usd NUMERIC,
    initial_volume_usd NUMERIC,
    initial_rank    INTEGER,
    peak_price_usd  NUMERIC,
    peak_price_date DATE,
    peak_mcap_usd   NUMERIC,
    cohort_half     TEXT,                       -- '2017H2', '2021H1', etc.
    notes           TEXT,
    inserted_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tokens_symbol ON tokens(symbol);
CREATE INDEX idx_tokens_cohort ON tokens(cohort_half);
CREATE INDEX idx_tokens_chain ON tokens(chain);
CREATE INDEX idx_tokens_category ON tokens(category);

-- Token-day panel: forward-filled from snapshots, with alive_flag
-- We don't store every day; we store one row per snapshot_date per token
-- Daily interpolation happens in-memory during analysis
CREATE TABLE token_panel (
    token_id        BIGINT NOT NULL REFERENCES tokens(token_id) ON DELETE CASCADE,
    obs_date        DATE NOT NULL,
    market_cap_usd  NUMERIC,
    price_usd       NUMERIC,
    volume_24h_usd  NUMERIC,
    rank            INTEGER,
    in_top_2000     BOOLEAN,
    drawdown_from_ath NUMERIC,                  -- (price - ath) / ath, negative number
    PRIMARY KEY (token_id, obs_date)
);

CREATE INDEX idx_panel_date ON token_panel(obs_date);

-- Death events: one row per (token, definition_variant)
-- Variants: 'primary' (180d), 'loose' (90d), 'strict' (365d), 'price_only' (180d price)
CREATE TABLE deaths (
    token_id            BIGINT NOT NULL REFERENCES tokens(token_id) ON DELETE CASCADE,
    definition_variant  TEXT NOT NULL,
    death_date          DATE,                   -- NULL = still alive (right-censored)
    is_dead             BOOLEAN NOT NULL,
    age_at_death_days   INTEGER,
    age_at_censor_days  INTEGER,
    computed_at         TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (token_id, definition_variant)
);

CREATE INDEX idx_deaths_variant ON deaths(definition_variant);
CREATE INDEX idx_deaths_dead ON deaths(is_dead);

-- Scrape log for debugging and resumability
CREATE TABLE scrape_log (
    id              BIGSERIAL PRIMARY KEY,
    source          TEXT NOT NULL,
    target_date     DATE,
    target_url      TEXT,
    status          TEXT NOT NULL,              -- 'ok', 'fail', 'skip', 'partial'
    rows_inserted   INTEGER,
    error_msg       TEXT,
    duration_ms     INTEGER,
    started_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scrape_log_target ON scrape_log(target_date, source);
