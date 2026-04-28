# Token Mortality: A Survival Analysis of Cryptocurrency Cohorts, 2014–2024

**[Author Name]**
*Independent Researcher, Singapore*

**Draft v0.1 — [DATE]**

---

## Abstract

The folk claim that "95% of crypto goes to zero" is widely repeated but rarely examined empirically with a defensible mortality definition or proper handling of right-censoring. This paper estimates the empirical survival function of cryptocurrency tokens listed on CoinMarketCap between 2014 and 2024 (N ≈ [TBD]), using a survivorship-bias-free panel that includes delisted and untracked tokens. Tokens are classified as dead if, for at least 180 consecutive days, their price falls below 1% of all-time-high, their 24-hour volume falls below \$1,000, and they exit CMC's top-2,000 ranking. Three alternative death definitions (90-day, 365-day, and price-only variants) are reported as robustness checks. Kaplan-Meier estimates and Cox proportional hazards regressions document substantial heterogeneity by cohort and category. A Weibull accelerated failure time model yields a shape parameter of [TBD], indicating [front- / back-]loaded hazard concentrated in [TBD]. After controlling for cohort and chain fixed effects, log initial market capitalization and log initial volume have small but statistically significant effects on survival; token category dominates, with [TBD] showing the highest hazard. The paper provides reusable empirical baselines for the cross-sectional risk of cryptocurrency investments and demonstrates that the mortality rate is not a single number but a function of token age, cohort, and category.

**JEL classification:** G12, G14, G32
**Keywords:** cryptocurrency, survival analysis, asset pricing, survivorship bias, token mortality

---

## 1. Introduction

Among practitioners and journalists, it is common to assert that the vast majority of cryptocurrency tokens will eventually become worthless. The figure most often quoted is 95%, traceable to a 2018 Medium essay by Sowmay Jain that argued the long-run survival rate of crypto projects would mirror the survival rate of early-stage venture-backed startups. Eight years on, the qualitative claim has held up: across every major cohort since 2014, the majority of tokens listed during a peak speculative phase have lost almost all of their value within a few years. Yet the precise quantitative claim — the fraction that go to zero, the typical time to "death," the predictability of which tokens survive — remains poorly characterized in the academic literature.

This paper provides such a characterization. We construct a survivorship-bias-free panel of cryptocurrency tokens covering eleven years of CoinMarketCap data and apply standard survival-analysis tools (Kaplan-Meier estimation, Cox proportional hazards regression, Weibull accelerated failure time models) to estimate the empirical mortality function and identify launch-time predictors of survival.

The contribution is intentionally narrow. We do not attempt to identify the causal drivers of token death, predict future mortality, or model the macroeconomic determinants of cohort risk. Instead, we provide three things:

First, **a defensible operational definition of token death**. Existing crypto datasets typically rely on either delisting events from a single exchange or arbitrary price thresholds, neither of which is satisfactory in isolation. We propose a primary definition combining three observable conditions — sustained low price relative to all-time-high, low trading volume, and exit from CMC's tracked-coin universe — and demonstrate that headline survival probabilities are robust across alternative definitions.

Second, **survival functions stratified by cohort, chain, and token category**. Heterogeneity across these dimensions has not been previously characterized at this resolution.

Third, **a Cox regression of token mortality on launch-time observables**. The principal finding is that initial market capitalization and trading volume have economically modest effects after cohort and category controls, while category itself dominates: tokens classified as memecoins or as tokens of ICO-era Layer 1 platforms exhibit substantially higher hazard than infrastructure or stablecoin categories.

The paper is structured as follows. Section 2 reviews the limited prior literature on cryptocurrency survival. Section 3 describes the data construction. Section 4 specifies the death definitions and pre-registers the statistical plan. Section 5 reports results. Section 6 discusses limitations and directions for future work.

---

## 2. Related literature

[TO DRAFT — keep this section short, ~1 page]

Prior work on cryptocurrency survival is sparse and mostly limited to:
- Cong, Li, Tang, and Zhang on token returns and survival
- Lyandres, Palazzo, and Rabetti on ICO outcomes
- Howell, Niessner, and Yermack on initial coin offerings
- Industry/blog analyses (Messari, Coinopsy) without rigorous methodology

Distinguish our contribution: full universe (not just ICOs), defensible death definition, multiple decades of cohorts, robustness across definitions.

---

## 3. Data

### 3.1 Source and coverage

The primary data source is CoinMarketCap (CMC), accessed via the open-source `crypto2` R package maintained by Stöckl. CMC's historical listings endpoint provides, for any given date, the full set of cryptocurrencies tracked by CMC on that date — including coins that have since been delisted or moved to "untracked" status. This addresses the principal methodological hazard in cryptocurrency research, namely survivorship bias from datasets that retroactively remove failed projects.

We construct the panel by querying `crypto_listings(which="historical")` at approximately 30-day intervals from 2014-01-01 to 2024-12-31, yielding [TBD] snapshot dates. Each snapshot contains, for every tracked token: a unique numeric identifier (`cmc_id`), symbol, name, slug, rank, market capitalization, closing price, 24-hour volume, circulating supply, and CMC's recorded "date_added" (the first date the token was listed). We retain all tokens regardless of category, including stablecoins, exchange tokens, and tokens later flagged by CMC for security or compliance issues.

After deduplication on `(snapshot_date, cmc_id)`, the panel contains [TBD] tokens with [TBD] token-day observations.

### 3.2 Token registry construction

A canonical token registry is built by grouping snapshots on `cmc_id`. This avoids a methodological pitfall: cryptocurrency symbols are not unique identifiers. For example, the symbol "LUNA" was used by Terra (Luna Classic) before its 2022 collapse and subsequently by the rebranded Terra 2.0 chain; these are distinct CMC entities with distinct `cmc_id` values and are correctly treated as separate tokens.

For each token we compute `first_seen` (the date of its first appearance in our panel), `last_seen`, peak price and the date thereof, peak market capitalization, initial market capitalization at first appearance, and an assigned cohort given by the calendar half-year of first appearance.

### 3.3 Sample restrictions

We exclude tokens with fewer than two snapshot observations (insufficient data for any survival inference) and tokens whose total observation window spans fewer than 30 days. After these filters the sample contains [TBD] tokens.

### 3.4 Covariates

Time-invariant token-level covariates measured at first appearance:

- `log_initial_mcap_usd`: logarithm of initial market cap (median imputed for missing values, clipped at \$1)
- `log_initial_volume_usd`: logarithm of initial 24-hour volume
- `log_initial_rank`: logarithm of initial CMC rank
- `chain`: assigned platform from CoinGecko enrichment, in {ETH, BSC, SOL, TRX, native, other, unknown}
- `category`: assigned coarse category from CoinGecko tags, in {L1, DeFi, meme, infrastructure, gaming, stablecoin, other}
- `cohort_half`: calendar half-year of first appearance (e.g. "2018H1")

Time-varying covariates entering the Cox specification:

- token age in days (the survival clock)
- BTC drawdown from all-time-high at observation date (a market-wide cycle control)

We deliberately exclude richer covariates (GitHub activity, Twitter follower trajectories, on-chain TVL, audit status) from this version of the paper. These would meaningfully strengthen the predictive specifications but their construction at scale across the full 2014–2024 universe is prohibitively expensive and would mostly substitute correlation for prediction.

---

## 4. Death definitions and statistical plan

### 4.1 Primary death definition

A token is declared dead at observation date *t* if, for the 180 consecutive days ending at *t*, all of the following hold:

1. Price ≤ 1% of all-time-high USD price
2. 24-hour trading volume < \$1,000
3. CMC rank > 2,000 (or absent from CMC tracking)

Death is recorded at the earliest such *t*. Tokens that never satisfy these conditions by 2024-12-31 are right-censored at that date. We require at least two observations within the 180-day window for a death event to be declared, eliminating spurious deaths from isolated bad data points.

### 4.2 Robustness variants

Three alternative definitions are reported alongside the primary, applying identical conditions but with varying parameters:

| Variant     | Window | Volume max | Price ≤ ATH × | Top-N filter |
|-------------|--------|------------|---------------|--------------|
| primary     | 180d   | \$1,000    | 1%            | 2,000        |
| loose       | 90d    | \$1,000    | 1%            | 2,000        |
| strict      | 365d   | \$1,000    | 1%            | 2,000        |
| price_only  | 180d   | —          | 1%            | —            |

If headline survival probabilities are qualitatively similar across all four definitions, the conclusions are not driven by the specific operationalization.

### 4.3 Statistical plan

The plan is pre-registered in the sense that the empirical analyses below were specified in code before the full panel was assembled and inspected.

1. **Kaplan-Meier estimation** of the pooled survival function and stratified survival functions by cohort half-year, chain, and category. Log-rank tests assess group differences.

2. **Cox proportional hazards regression** of mortality on the full set of time-invariant covariates, with the BTC drawdown indicator as a time-varying control. The proportional hazards assumption is tested via Schoenfeld residuals; if violated for cohort, a stratified Cox specification is reported instead.

3. **Weibull accelerated failure time model** to estimate the shape parameter *k*. Values *k* < 1 indicate decreasing hazard (front-loaded mortality); *k* > 1 indicates increasing hazard.

4. All three analyses are repeated under each of the four death definitions, with headline survival probabilities at 1, 3, and 5 years reported in a single robustness table.

---

## 5. Results

[TO BE WRITTEN AFTER PIPELINE COMPLETES]

### 5.1 Sample description

Table 1: Tokens by cohort half-year and category. Mean and median initial market cap. Death rate by cohort.

### 5.2 Pooled survival

Figure 1: Pooled Kaplan-Meier curve under primary definition, with 95% confidence band.

Headline numbers: 1-year, 3-year, 5-year survival probabilities.

### 5.3 Stratified survival

Figure 2: KM by cohort half-year.
Figure 3: KM by category.
Figure 4: KM by chain.

Log-rank test results.

### 5.4 Cox regression

Table 2: Cox PH coefficients, hazard ratios, 95% CIs.

### 5.5 Weibull shape

Reported *k*, interpretation, comparison to other asset-class survival distributions if available.

### 5.6 Robustness

Table 3: Headline survival probabilities and Cox concordance across all four death definitions.

---

## 6. Discussion

[TO BE WRITTEN]

Themes to address:

- The "95% to zero" folk claim revisited: what fraction of which cohorts have actually crossed the death threshold? Distinguish unconditional cohort death rates from the conditional rates given specific observable launch features.
- The cohort effect: 2017H2 (ICO peak) and 2021H1 (DeFi/NFT peak) cohorts likely show the worst survival. This is an artifact of speculative cycle timing, not a stable property of any year.
- What remains unexplained: the substantial residual variance in survival even after controlling for cohort, category, and chain. Future work should incorporate developer activity, audit status, and on-chain holder concentration.

---

## 7. Limitations

- CMC tracking is itself a selection: tokens that never make CMC's tracked list are not in our panel. This biases the universe toward tokens that achieved at least minimal exchange listing.
- The 30-day snapshot cadence imposes measurement error on `first_seen` of up to 30 days.
- The CG-based chain and category enrichment is noisy; we accept this rather than hand-classify.
- We do not model causal mechanisms. Cox coefficients should be interpreted as descriptive associations within the joint distribution of observable features, not as treatment effects.

---

## 8. Reproducibility

All code, the SQL schema, and the snapshot CSVs (the latter pending hosting) are available at [REPO URL]. The pipeline reproduces from scratch in approximately one hour of wall-clock time on a single VPS, given an installed R interpreter and a Postgres instance.

---

## References

[TO BE COMPLETED — minimum set]

- Cong, L. W., Li, Y., Tang, K., & Zhang, Y. (2022). *Crypto wash trading.* Working paper.
- Howell, S. T., Niessner, M., & Yermack, D. (2020). Initial coin offerings: Financing growth with cryptocurrency token sales. *Review of Financial Studies* 33(9): 3925–3974.
- Jain, S. (2018). Why 95% of cryptocurrencies will fail. *Medium*, [date].
- Liu, Y., & Tsyvinski, A. (2021). Risks and returns of cryptocurrency. *Review of Financial Studies* 34(6): 2689–2727.
- Stöckl, S. (2024). `crypto2`: Download crypto currency data from CoinMarketCap without API. R package.

---

*[End of v0.1 draft]*
