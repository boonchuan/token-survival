"""
Survival analysis for the token mortality study.

Outputs:
- KM curves: pooled, by cohort, by category, by chain (PNG)
- Log-rank tests for each grouping (text report)
- Cox PH regression with covariates (text report + coefficients CSV)
- Weibull AFT shape parameter (text report)
- Robustness table across all 4 death definitions

Run after compute_deaths.py.
"""
import datetime as dt
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter, CoxPHFitter, WeibullAFTFitter
from lifelines.statistics import multivariate_logrank_test

from config import DATA_DIR, get_logger, get_cursor, DEATH_DEFINITIONS

log = get_logger("survival_analysis")
OUT_DIR = DATA_DIR / "results"
OUT_DIR.mkdir(exist_ok=True)


def load_dataset(variant: str = "primary") -> pd.DataFrame:
    """One row per token with duration, event, and covariates."""
    sql = """
        SELECT
            t.token_id, t.symbol, t.cohort_half, t.chain, t.category,
            t.initial_mcap_usd, t.initial_volume_usd, t.initial_rank,
            t.first_seen, t.last_seen,
            d.is_dead, d.death_date, d.age_at_death_days, d.age_at_censor_days
        FROM tokens t
        JOIN deaths d USING (token_id)
        WHERE d.definition_variant = %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (variant,))
        cols = [c.name for c in cur.description]
        rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=cols)

    df["duration"] = np.where(
        df["is_dead"], df["age_at_death_days"], df["age_at_censor_days"]
    ).astype(float)
    df["event"] = df["is_dead"].astype(int)

    # Drop tokens with non-positive duration (data artifacts)
    n0 = len(df)
    df = df[df["duration"] > 0].copy()
    if len(df) < n0:
        log.warning(f"Dropped {n0 - len(df)} rows with non-positive duration")

    # Log-transform mcap/volume; impute NaNs with column median pre-log
    for col in ["initial_mcap_usd", "initial_volume_usd"]:
        med = df[col].median()
        df[col] = df[col].fillna(med).clip(lower=1.0)
        df[f"log_{col}"] = np.log(df[col])

    df["log_initial_rank"] = np.log(df["initial_rank"].fillna(2000).clip(lower=1.0))

    return df


def km_pooled(df: pd.DataFrame, label: str):
    kmf = KaplanMeierFitter()
    kmf.fit(df["duration"], df["event"], label="All tokens")
    fig, ax = plt.subplots(figsize=(8, 5))
    kmf.plot_survival_function(ax=ax)
    ax.set_xlabel("Days since first listing")
    ax.set_ylabel("Survival probability")
    ax.set_title(f"Pooled KM survival, definition='{label}'")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"km_pooled_{label}.png", dpi=150)
    plt.close(fig)

    # 1y / 3y / 5y survival
    surv = kmf.survival_function_
    pts = {}
    for years in [1, 3, 5]:
        days = years * 365
        if surv.index.max() >= days:
            v = float(kmf.predict(days))
            pts[f"S({years}y)"] = v
    return pts


def km_by_group(df: pd.DataFrame, group_col: str, label: str, top_k: int = 8):
    """KM curves stratified by group_col; logrank test reported."""
    counts = df[group_col].value_counts()
    keep = counts.head(top_k).index.tolist()
    sub = df[df[group_col].isin(keep)].copy()
    if sub.empty:
        return None

    fig, ax = plt.subplots(figsize=(9, 6))
    for grp in keep:
        mask = sub[group_col] == grp
        if mask.sum() < 30:
            continue
        kmf = KaplanMeierFitter()
        kmf.fit(sub.loc[mask, "duration"], sub.loc[mask, "event"],
                label=f"{grp} (n={mask.sum()})")
        kmf.plot_survival_function(ax=ax, ci_show=False)
    ax.set_xlabel("Days since first listing")
    ax.set_ylabel("Survival probability")
    ax.set_title(f"KM by {group_col}, definition='{label}'")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"km_by_{group_col}_{label}.png", dpi=150)
    plt.close(fig)

    lr = multivariate_logrank_test(sub["duration"], sub[group_col], sub["event"])
    return {"chi2": float(lr.test_statistic), "p": float(lr.p_value), "df": lr.degrees_of_freedom}


def cox_regression(df: pd.DataFrame, label: str):
    feats = ["log_initial_mcap_usd", "log_initial_volume_usd", "log_initial_rank"]
    cat_dummies = pd.get_dummies(df[["chain", "category", "cohort_half"]],
                                 drop_first=True, dummy_na=False)
    X = pd.concat([df[feats + ["duration", "event"]], cat_dummies], axis=1)
    X = X.dropna(subset=["duration", "event"])

    cph = CoxPHFitter(penalizer=0.01)  # small ridge for numerical stability
    try:
        cph.fit(X, duration_col="duration", event_col="event", show_progress=False)
    except Exception as e:
        log.error(f"Cox fit failed: {e}")
        return None

    cph.summary.to_csv(OUT_DIR / f"cox_summary_{label}.csv")
    log.info(f"Cox concordance ({label}): {cph.concordance_index_:.4f}")
    return {"c_index": float(cph.concordance_index_),
            "n": int(cph._n_examples),
            "events": int(cph.event_observed.sum())}


def weibull_aft(df: pd.DataFrame, label: str):
    feats = ["log_initial_mcap_usd", "log_initial_volume_usd"]
    X = df[feats + ["duration", "event"]].dropna()

    aft = WeibullAFTFitter()
    try:
        aft.fit(X, duration_col="duration", event_col="event", show_progress=False)
    except Exception as e:
        log.error(f"Weibull AFT failed: {e}")
        return None

    # rho_ in lifelines parametrization is the shape; lambda_ is scale
    # k > 1 = increasing hazard, k < 1 = decreasing hazard, k = 1 = constant
    shape = float(aft.summary.loc["rho_", "Intercept"]["coef"])  # log-scale
    shape_actual = np.exp(shape)
    log.info(f"Weibull shape k={shape_actual:.4f} (definition={label})")
    return {"weibull_k": shape_actual}


def run_all():
    summary = []
    for variant in DEATH_DEFINITIONS.keys():
        log.info(f"=== Running variant: {variant} ===")
        df = load_dataset(variant)
        if df.empty:
            log.warning(f"No data for {variant}")
            continue
        log.info(f"  n={len(df)}, events={df['event'].sum()}")

        s = {"variant": variant, "n": len(df), "events": int(df["event"].sum())}
        s.update(km_pooled(df, variant) or {})

        for grp in ["cohort_half", "category", "chain"]:
            r = km_by_group(df, grp, variant)
            if r:
                s[f"logrank_{grp}_p"] = r["p"]

        cox = cox_regression(df, variant)
        if cox:
            s["cox_c"] = cox["c_index"]

        wb = weibull_aft(df, variant)
        if wb:
            s["weibull_k"] = wb["weibull_k"]

        summary.append(s)

    pd.DataFrame(summary).to_csv(OUT_DIR / "summary_table.csv", index=False)
    log.info("Summary table written")


if __name__ == "__main__":
    run_all()
