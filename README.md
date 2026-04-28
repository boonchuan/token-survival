# Token Survival Analysis

**Working title:** *Token Mortality: A Survival Analysis of Cryptocurrency Cohorts, 2014–2024*

Empirical survival functions for cryptocurrency tokens, with cohort-, chain-,
and launch-feature-conditional Cox PH and Weibull AFT models. Source data:
CoinMarketCap historical listings via the `crypto2` R package
(survivorship-bias-free, includes delisted and untracked coins). N = 28,123
tokens across 134 monthly snapshots, 2014-01 to 2024-12.

## Headline result

61.5% of tokens are dead under our primary definition. 5-year survival is
17.0%, robust to alternative operationalizations (range 11.3% to 22.4% across
four definitions). Cohorts older than 5 years show 80–95% mortality, supporting
the "95% will go to zero" folklore as a long-run cohort claim while refuting it
as a near-term population statement.

## Sample frame

- Universe: tokens listed on CoinMarketCap, 2014-01-01 → 2024-12-04
- Snapshot cadence: ~30 days (134 dates)
- Final N: 28,123 distinct tokens after deduplication

## Death definitions

A token is dead at time *t* if all relevant conditions hold for the variant's
window (see `src/config.py` `DEATH_DEFINITIONS`):

| Variant      | Window | Vol max | ATH ratio max | Top-N rank |
|--------------|--------|---------|---------------|------------|
| primary      | 180d   | $1,000  | 1%            | 2,000      |
| loose        | 90d    | $1,000  | 1%            | 2,000      |
| strict       | 365d   | $1,000  | 1%            | 2,000      |
| price_only   | 180d   | —       | 1%            | —          |
| feder_simple | volume <= 1% peak, with resurrection at >= 10% peak |

`primary` is the headline; the others are robustness checks. `feder_simple`
re-implements Feder et al. (2018) for direct prior-work comparison.

A token also counts as dead if its `last_obs` precedes the study's end by at
least the window length and it never reappears (the "Path B" disappearance
rule, accounting for ~85% of declared deaths under the primary definition).

## Pipeline

```
run_pipeline.sh
  sql/schema.sql               (DB setup; DROPs + CREATEs)
  src/fetch_cmc_listings.R     (crypto2 -> per-date CSVs in data/raw/)
  src/ingest_cmc_listings.py   (CSVs -> cmc_snapshots)
  src/build_panel.py           (cmc_snapshots -> tokens, token_panel)
  src/cg_enrichment.py         (CG bulk endpoint -> chain & category)
  src/compute_deaths.py        (4 primary variants -> deaths)
  src/feder_compare.py         (Feder simplified definition for comparison)
  src/survival_analysis.py     (KM, Cox, Weibull -> data/results/)
```

Each stage is idempotent. Re-running rebuilds derived tables from raw snapshots.

## Setup

```bash
# Postgres
sudo -u postgres createdb token_survival
sudo -u postgres psql -c "CREATE ROLE \"delta-dev\" WITH LOGIN PASSWORD '...';"
sudo -u postgres psql -c "ALTER DATABASE token_survival OWNER TO \"delta-dev\";"

# Python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# R (one-time)
sudo apt install -y r-base r-base-dev libcurl4-openssl-dev libxml2-dev libssl-dev
sudo Rscript -e 'install.packages(c("crypto2","dplyr"), repos="https://cloud.r-project.org")'

# Env vars
export TS_DB_HOST=localhost
export TS_DB_NAME=token_survival
export TS_DB_USER=delta-dev
export TS_DB_PASS=...
export PGPASSWORD=...

./run_pipeline.sh
```

## Timing (on a small VPS)

| Stage                   | Wall time |
|-------------------------|-----------|
| fetch_cmc_listings (R)  | ~30 min   |
| ingest_cmc_listings.py  | ~2 min    |
| build_panel.py          | ~1 min    |
| cg_enrichment.py        | ~30 sec   |
| compute_deaths.py       | ~30 sec   |
| feder_compare.py        | ~10 sec   |
| survival_analysis.py    | ~1 min    |

Total ~35 min wall clock, dominated by the crypto2 fetch.

## Outputs

- `data/raw/listings_YYYYMMDD.csv` — per-date snapshots from crypto2
- `data/results/km_pooled_*.png` — pooled Kaplan-Meier curves
- `data/results/km_by_cohort_half_*.png` — cohort-stratified KM curves
- `data/results/km_by_chain_*.png` — chain-stratified KM curves
- `data/results/km_by_category_*.png` — category-stratified KM curves
- `data/results/cox_summary_*.csv` — Cox coefficient tables
- `data/results/summary_table.csv` — master summary across variants
- `paper/draft_v*.md` — paper drafts in markdown

## Reproducibility

The pipeline reproduces from scratch given the dependencies listed above. The
crypto2 endpoint accesses CMC's public web API and does not require an API key.
Snapshot CSVs are not committed to the repository (~1.5 GB total); regenerate
via `Rscript src/fetch_cmc_listings.R`.
