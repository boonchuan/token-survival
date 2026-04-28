#!/usr/bin/env bash
# Full reproducibility pipeline (v2 — crypto2-based).
# Run from ~/token_survival on the VPS.
# Assumes: postgres up, db `token_survival` exists, env vars set, R installed.

set -euo pipefail

PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJ_DIR"

# 0. Ensure schema (idempotent; DROPs and CREATEs)
psql -h "${TS_DB_HOST:-localhost}" -U "${TS_DB_USER:-delta-dev}" \
     -d "${TS_DB_NAME:-token_survival}" \
     -f sql/schema.sql

# 1. Fetch via crypto2 (R) -> CSVs in data/raw/
#    Resumable: skips dates whose CSV already exists with size > 100 bytes.
Rscript src/fetch_cmc_listings.R

# 2. Ingest CSVs into cmc_snapshots
python3 src/ingest_cmc_listings.py

# 3. Build canonical tokens + token_panel
python3 src/build_panel.py

# 4. Enrich with CG chain/category tags (optional)
python3 src/cg_enrichment.py || echo "CG enrichment failed (non-fatal)"

# 5. Compute deaths under all 4 definitions
python3 src/compute_deaths.py

# 6. Survival analysis
python3 src/survival_analysis.py

echo "Pipeline complete. Results in data/results/"
