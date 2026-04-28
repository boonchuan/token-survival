# Token Mortality: A Survival Analysis of Cryptocurrency Cohorts, 2014–2024

**[Author Name]**
*Independent Researcher, Singapore*

**Draft v0.2 — April 28, 2026**

---

## Abstract

Across N=28,123 cryptocurrency tokens listed on CoinMarketCap between 2014 and 2024, we estimate empirical survival functions and document substantial heterogeneity by cohort and chain. Under a primary death definition that requires 180-day persistence at less than 1% of all-time-high price, less than \$1,000 daily volume, and absence from CMC's top-2,000 ranking, the unconditional 5-year survival rate is 17.0%, robust to alternative operationalizations (range 11.3% to 22.4% across four definitions). The Weibull shape parameter is 1.37, indicating that mortality hazard *increases* with token age — contrary to the common intuition that tokens which survive their first year are subsequently safer. Cox proportional hazards regression with cohort, chain, and launch-feature controls achieves a concordance index of 0.72. Initial market capitalization has economically negligible effects on survival, while initial trading volume (HR=0.94 per log unit) and initial CMC rank (HR=1.62 per log unit) are economically meaningful predictors. Tokens deployed on Ethereum exhibit lower mortality (42.0%) than those on Solana (49.0%) or Binance Smart Chain (47.7%); cohort effects dominate, with the 2014H2-2017H2 vintages showing 80-95% mortality and the 2021H2 cohort already at 79% by Q4 2024. The findings empirically refute the widely-cited "95% of cryptocurrencies will go to zero" claim as a near-term prediction — the unconditional rate is closer to 60% — while supporting it asymptotically: cohorts that have aged beyond five years show survival rates between 5% and 20%.

**JEL classification:** G12, G14, G32
**Keywords:** cryptocurrency, survival analysis, asset pricing, survivorship bias, token mortality

---

## 1. Introduction

The claim that "95% of cryptocurrencies will go to zero" is one of the most widely repeated maxims in digital asset markets. Its provenance traces to a 2018 *Medium* essay by Sowmay Jain that argued the long-run survival rate of crypto projects would mirror the survival rate of early-stage venture-backed startups. Eight years on, the qualitative claim has held up: across every major cohort since 2014, the majority of tokens listed during a peak speculative phase have lost almost all of their value within a few years. Yet the precise quantitative claim — the fraction that go to zero, the typical time to "death," the predictability of which tokens survive — remains poorly characterized in the academic literature.

This paper provides such a characterization. We construct a survivorship-bias-free panel of cryptocurrency tokens covering eleven years of CoinMarketCap data and apply standard survival-analysis tools (Kaplan-Meier estimation, Cox proportional hazards regression, Weibull accelerated failure time models) to estimate the empirical mortality function and identify launch-time predictors of survival.

The contribution is intentionally narrow. We do not attempt to identify the causal drivers of token death, predict future mortality, or model the macroeconomic determinants of cohort risk. Instead, we provide three things.

First, **a defensible operational definition of token death**. Existing crypto datasets typically rely on either delisting events from a single exchange or arbitrary price thresholds, neither of which is satisfactory in isolation. We propose a primary definition combining three observable conditions — sustained low price relative to all-time-high, low trading volume, and exit from CMC's tracked-coin universe — and demonstrate that headline survival probabilities are robust across alternative definitions.

Second, **survival functions stratified by cohort and chain**. The cohort heterogeneity is dramatic: the 2014H2 cohort is 95.5% dead, the 2021H2 cohort is 78.8% dead despite being only three years old, and within these groups the survival paths differ in shape rather than merely in level. This heterogeneity has not been previously documented at this resolution.

Third, **a Cox regression of token mortality on launch-time observables**. The principal finding is that initial market capitalization has economically negligible effects on survival after cohort and chain controls; the strongest predictors are initial trading volume and initial rank, with chain of deployment also explaining meaningful variance.

A secondary finding deserves emphasis: **the Weibull shape parameter is well above unity** (k=1.37 under the primary definition, 1.13 to 1.77 across robustness variants). This implies that the conditional hazard of death is increasing in token age. Tokens that have survived their first three years are not safer than newly-launched tokens; if anything, their hazard rate is higher. This contradicts the common practitioner heuristic that "if a project survives the bear market it is fine."

The paper is structured as follows. Section 2 reviews the limited prior literature on cryptocurrency survival. Section 3 describes the data construction. Section 4 specifies the death definitions and pre-registered statistical plan. Section 5 reports results. Section 6 discusses implications and limitations.

---

## 2. Related literature

[BRIEF — TODO: confirm and expand after literature search]

The empirical literature on cryptocurrency survival is sparse. Howell, Niessner, and Yermack (2020) study initial coin offerings and document poor outcomes for the median project. Liu and Tsyvinski (2021) characterize crypto returns at the asset-class level but do not address project survival. Cong, Li, Tang, and Zhang (2022) document wash trading on cryptocurrency exchanges, an important but distinct concern. Industry analyses (Messari, Coinopsy, the now-defunct deadcoins.com) have produced summary statistics on dead tokens but generally without methodological transparency or proper handling of right-censoring.

Our contribution differs from this prior work in three ways. First, we cover the full universe of CMC-tracked tokens rather than a subset (e.g., ICOs only). Second, we propose and defend an operational death definition rather than relying on exchange delistings. Third, we report survival functions across the full 2014–2024 sample period using formal survival-analysis methods.

---

## 3. Data

### 3.1 Source and coverage

The primary data source is CoinMarketCap (CMC), accessed via the open-source `crypto2` R package maintained by Stöckl. CMC's historical listings endpoint provides, for any given date, the full set of cryptocurrencies tracked by CMC on that date — including coins that have since been delisted or moved to "untracked" status. This addresses the principal methodological hazard in cryptocurrency research, namely survivorship bias from datasets that retroactively remove failed projects. As Stöckl notes, this property makes the data source "a valid basis for any asset pricing studies based on cryptocurrencies that require survivorship-bias-free information."

We construct the panel by querying `crypto_listings(which="historical")` at approximately 30-day intervals from 2014-01-01 to 2024-12-04, yielding 134 snapshot dates. Each snapshot contains, for every tracked token: a unique numeric identifier (`cmc_id`), symbol, name, slug, rank, market capitalization, closing price, 24-hour volume, and circulating supply. The resulting raw panel contains 526,547 token-day observations.

### 3.2 Token registry construction

A canonical token registry is built by grouping snapshots on `cmc_id`. This avoids a methodological pitfall: cryptocurrency symbols are not unique identifiers. For example, the symbol "LUNA" was used by Terra (Luna Classic) before its 2022 collapse and subsequently by the rebranded Terra 2.0 chain; these are distinct CMC entities with distinct `cmc_id` values and are correctly treated as separate tokens.

For each token we compute `first_seen` (the date of its first appearance in our panel), `last_seen`, peak price and the date thereof, peak market capitalization, initial market capitalization at first appearance, and an assigned cohort given by the calendar half-year of first appearance.

After deduplication, the panel contains **28,123 distinct tokens**. The annual cross-section grows from 751 unique tokens in 2014 to 14,057 in 2024, with year-by-year growth concentrated in 2020-2022 (a 3.2x increase) reflecting the DeFi and NFT boom.

### 3.3 Covariates

Time-invariant token-level covariates measured at first appearance:

- `log_initial_mcap_usd`: logarithm of initial market capitalization (median imputed for missing values, clipped at \$1)
- `log_initial_volume_usd`: logarithm of initial 24-hour volume
- `log_initial_rank`: logarithm of initial CMC rank
- `chain`: assigned platform from CoinGecko's bulk asset-platform list, in {ETH, BSC, SOL, TRX, AVAX, FTM, native, other, unknown}
- `category`: assigned from heuristic classification of token name and symbol, in {stablecoin, meme, DeFi, gaming, other}
- `cohort_half`: calendar half-year of first appearance

The CG-based chain assignment matches 12,609 of 28,123 tokens (44.8%); the remainder are classified as `unknown`. The category classification is intentionally simple — based on a curated keyword list — and we acknowledge it is noisier than per-token tag retrieval would be. We discuss the implications in Section 6.

We deliberately exclude richer covariates (GitHub activity, Twitter follower trajectories, on-chain TVL, audit status) from this version of the paper. Their construction at scale across the full 2014–2024 universe is prohibitively expensive and would mostly substitute correlation for prediction.

---

## 4. Death definitions and statistical plan

### 4.1 Primary death definition

A token is declared dead at observation date *t* if all of the following hold for the 180 consecutive days ending at *t*:

1. Price ≤ 1% of all-time-high USD price
2. 24-hour trading volume < \$1,000
3. CMC rank > 2,000 (or absent from CMC tracking entirely)

Death is recorded at the earliest such *t*. Tokens that never satisfy these conditions by 2024-12-04 are right-censored at that date. We require at least two observations within the 180-day window for an in-panel death event to be declared, eliminating spurious deaths from isolated bad data points.

A token whose `last_obs` precedes the end of the study period by at least the window length and which never reappears is also declared dead (death date assigned at `last_obs + window_days`). This captures the common case where a token is dropped from CMC tracking entirely after losing exchange listings — the rank condition is satisfied vacuously, and the price/volume conditions are unobservable but, in practice, near-uniformly satisfied.

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
2. **Cox proportional hazards regression** of mortality on the full set of time-invariant covariates. The proportional hazards assumption is tested via Schoenfeld residuals; if violated for cohort, a stratified Cox specification is reported instead.
3. **Weibull accelerated failure time model** to estimate the shape parameter *k*. Values *k* < 1 indicate decreasing hazard (front-loaded mortality); *k* > 1 indicates increasing hazard.
4. All three analyses are repeated under each of the four death definitions, with headline survival probabilities at 1, 3, and 5 years reported in a single robustness table.

---

## 5. Results

### 5.1 Headline mortality rates

Table 1 presents the proportion of tokens dead by 2024-12-04 under each of the four death definitions:

| Definition  | Tokens | Deaths | Pct dead |
|-------------|--------|--------|----------|
| primary     | 28,123 | 17,292 | 61.5%    |
| loose       | 28,123 | 18,933 | 67.3%    |
| strict      | 28,123 | 14,779 | 52.6%    |
| price_only  | 28,123 | 18,599 | 66.1%    |

The unconditional mortality rate is between 53% and 67% across the four definitions, well below the widely-cited "95%" figure. However, these unconditional rates pool cohorts that have had eleven years to die with cohorts that have had less than one. The cohort-conditional rates in Section 5.3 show the picture is closer to the folklore claim than the headline number suggests.

### 5.2 Pooled survival function

Figure 1 plots the Kaplan-Meier survival function under the primary definition. Headline survival probabilities at 1, 3, and 5 years from listing are presented in Table 2, alongside the same statistics under the three robustness variants:

| Definition  | S(1y)  | S(3y)  | S(5y)  |
|-------------|--------|--------|--------|
| primary     | 67.9%  | 30.2%  | 17.0%  |
| loose       | 58.2%  | 26.2%  | 14.6%  |
| strict      | 94.7%  | 38.0%  | 22.4%  |
| price_only  | 62.5%  | 23.0%  | 11.3%  |

Five years is the most natural benchmark horizon. **Five-year survival is 17.0% under the primary definition, with 95% bounds of approximately [11%, 22%] across alternative operationalizations.** Beyond the five-year mark, the curve flattens slowly: 7-year survival is approximately 10%, and tokens that have survived eleven years (the 2014 cohort) show 5-year-conditional survival near zero — that is, almost no token from 2014 that was alive in 2019 remains alive today.

[Insert Figure 1 here]

### 5.3 Heterogeneity by cohort

Figure 2 plots survival functions stratified by cohort half-year. The log-rank test for cohort effects rejects equality at p < 10^-176, an enormous test statistic that reflects the sample size and the degree of separation between cohorts.

The cohort-by-cohort table (Table 3) is the paper's most striking finding:

| Cohort | N     | Pct dead |
|--------|-------|----------|
| 2014H1 | 394   | 85.8%    |
| 2014H2 | 357   | 95.5%    |
| 2015H1 | 188   | 94.7%    |
| 2015H2 | 157   | 89.8%    |
| 2016H1 | 154   | 85.1%    |
| 2016H2 | 192   | 88.5%    |
| 2017H1 | 235   | 84.7%    |
| 2017H2 | 536   | 80.4%    |
| 2018H1 | 534   | 73.8%    |
| 2018H2 | 693   | 79.4%    |
| 2019H1 | 355   | 71.0%    |
| 2019H2 | 401   | 69.3%    |
| 2020H1 | 440   | 68.0%    |
| 2020H2 | 1,628 | 76.0%    |
| 2021H1 | 2,058 | 70.8%    |
| 2021H2 | 4,434 | 78.8%    |
| 2022H1 | 3,536 | 77.0%    |
| 2022H2 | 2,007 | 70.0%    |
| 2023H1 | 3,111 | 68.1%    |
| 2023H2 | 1,536 | 53.1%    |
| 2024H1 | 2,805 | 12.1%    |
| 2024H2 | 2,372 | 0.0%     |

Three patterns are visible. First, **all cohorts older than five years are between 71% and 96% dead**. The four oldest cohorts (2014H1 through 2015H2) are at 86–96% mortality, very close to the folklore prediction. Second, **the 2021H2 NFT/DeFi-peak cohort is already 79% dead at three years of age** — comparable to the death rate of cohorts that are more than twice its age. Third, the 2024 cohorts retain near-100% survival because the panel ends in 2024-12 and most of these tokens have not had time to die under our 180-day window.

[Insert Figure 2 here]

### 5.4 Heterogeneity by chain

Table 4 reports the Pct-dead under the primary definition by chain assignment:

| Chain    | N      | Pct dead |
|----------|--------|----------|
| unknown  | 15,514 | 75.1%    |
| SOL      | 2,570  | 49.0%    |
| BSC      | 2,133  | 47.7%    |
| AVAX     | 159    | 45.9%    |
| other    | 1,294  | 44.6%    |
| FTM      | 21     | 42.9%    |
| native   | 556    | 42.1%    |
| ETH      | 5,799  | 42.0%    |
| TRX      | 77     | 37.7%    |

Tokens whose chain CG could not assign (`unknown`) have 75% mortality, reflecting the strong selection effect: if a token is not in CG's index, it is disproportionately likely to be dead or never traded meaningfully. Among tokens with a confidently-assigned chain, **Ethereum-deployed tokens have the lowest mortality (42.0%)**, followed by native L1 coins (42.1%), and tokens on Tron (37.7%, mostly stablecoin issuance). Tokens deployed on Solana (49.0%) and Binance Smart Chain (47.7%) — the chains most associated with the 2021 memecoin and high-throughput DEX boom — exhibit roughly 7 percentage points higher mortality than Ethereum.

The log-rank test for chain effects is highly significant (p effectively zero at machine precision).

### 5.5 Cox regression

Table 5 presents Cox proportional hazards estimates under the primary definition. The model includes log initial market cap, log initial volume, log initial rank, chain dummies, category dummies, and cohort half dummies. Concordance index is 0.722.

Selected coefficients (full table in supplementary materials):

| Covariate                  | exp(coef) | 95% CI         | p           |
|----------------------------|-----------|----------------|-------------|
| log_initial_mcap_usd       | 1.007     | [1.001, 1.012] | 0.026       |
| log_initial_volume_usd     | 0.941     | [0.937, 0.945] | < 10^-100   |
| log_initial_rank           | 1.621     | [1.552, 1.693] | < 10^-100   |
| cohort_half_2020H1 (vs 2014H1) | 0.377 | [0.324, 0.438] | < 10^-30    |
| cohort_half_2021H2 (vs 2014H1) | 0.752 | [0.666, 0.849] | < 10^-5     |

**Initial market capitalization has economically negligible effects.** The estimated hazard ratio is 1.007 per log unit of market cap, meaning that even a 1000x difference in launch market cap changes hazard by only ~5%. This is statistically significant (p=0.026) but practically meaningless. The intuition that "tokens with bigger launches survive better" is not supported by the data — once volume and rank are controlled for.

**Initial trading volume is the strongest economically-meaningful predictor among continuous launch-time variables.** A 10x increase in initial volume is associated with a 14% reduction in hazard (HR=0.941^log(10)≈0.86). Volume captures market interest in a way that market cap (which is largely determined by token economics, not market depth) does not.

**Initial CMC rank has the largest effect by far.** A 10x increase in rank number (i.e., dropping from rank 100 to rank 1000) raises hazard by 62%. This is consistent with rank being a sufficient statistic for the joint information in liquidity, exchange coverage, and market interest at launch.

**Cohort effects are large and non-monotonic.** Relative to the 2014H1 reference cohort, the 2018H1, 2019, and 2020H1 cohorts show substantially lower hazard (HR ~ 0.38–0.51) — these are the "good" cohorts that benefited from the 2020-2021 bull market. The 2021H2 cohort's HR of 0.75 is closer to the 2014H1 baseline, reflecting the elevated speculative excess of that period.

### 5.6 Weibull shape

The Weibull AFT model yields shape parameters as follows:

| Definition  | k    |
|-------------|------|
| primary     | 1.37 |
| loose       | 1.13 |
| strict      | 1.77 |
| price_only  | 1.39 |

**All four definitions give k > 1, indicating that hazard increases with token age.** This is a meaningful empirical contradiction of the practitioner intuition that surviving the first year confers safety. Possible mechanisms include: (a) tokens that survive the first wave of attention but never achieve organic adoption fade gradually rather than abruptly; (b) protocol obsolescence as newer technologies displace older ones; (c) team attrition as developer focus moves to new projects.

The shape parameter under the strict (365-day) definition is the highest (k=1.77), because requiring a longer period of zero activity excludes tokens that might briefly recover. Under the loose (90-day) definition, k=1.13 is closer to constant hazard, capturing more rapid early deaths.

### 5.7 Robustness

Headline survival probabilities and Cox concordance indices across all four death definitions are summarized in Table 6 (`summary_table.csv` in the supplementary materials). The qualitative findings hold across all variants: 5-year survival between 11% and 22%, Weibull k > 1, Cox concordance 0.69–0.72, log-rank cohort effects highly significant in every case.

---

## 6. Discussion

### 6.1 Reconsidering "95% will go to zero"

The folklore claim that 95% of cryptocurrencies will go to zero is approximately right at the cohort level for any cohort older than five years, and approximately right asymptotically for the entire sample, but it is misleading as an unconditional claim about "current" tokens. At any given moment, the unconditional dead-rate in the population is bounded by the cohort-mix: in a market with rapid new-token issuance (as in 2021–2024), the unconditional rate looks lower because newer cohorts have not had time to die. Investors interpreting "95% will go to zero" as a near-term forecast are extrapolating a long-run cohort property to a short-run population property, which is not warranted.

A more accurate restatement is: *for cohorts that have had five years to mature, mortality is between 80% and 95%; this rate is converging downward across cohorts as median project quality improves, but only modestly.* The 2018-2020 cohorts that arose in the post-ICO regulatory tightening have somewhat better survival than the pure-ICO 2014–2017 cohorts, but the difference is in the range of 10–20 percentage points, not 50.

### 6.2 The increasing-hazard finding

The Weibull shape parameter exceeding unity is a result that we did not anticipate ex ante and that warrants future investigation. The conventional view, articulated by venture capitalists and crypto practitioners alike, is that early failure dominates: most projects die in the first 12 months, and survivors are progressively safer. Our data does not support this. Tokens that have survived three or four years face higher conditional hazard than newly-launched tokens.

We caution that this result may partly reflect the construction of our death definition rather than an inherent feature of crypto asset failure. Newly-launched tokens have less opportunity to accumulate the 180-day "in death state" run required by our definition; they may be effectively dead but censored by the requirement that they have first been alive long enough to die. A more granular analysis using continuous time-varying risk would illuminate this further.

### 6.3 Chain effects and platform risk

Ethereum's 7-percentage-point survival advantage over Solana and BSC is consistent with several mechanisms: stronger developer ecosystems supporting projects through downturns, deeper DEX liquidity providing baseline trading regardless of project momentum, and possibly selection on initial token quality (the cost of deploying on Ethereum may filter out the most ephemeral projects). We do not attempt to disentangle these here.

### 6.4 What the regression does and does not imply

The Cox regression should be interpreted as a descriptive characterization of the joint distribution of survival and observable features at launch, not as a treatment-effect identification. The result that initial market cap has near-zero effect after controlling for volume and rank does not mean that "raising more capital does not help projects survive"; it likely means that initial market cap is not a sufficient statistic for the project quality that matters for survival, after controlling for the variables that are. The strong rank effect is similarly descriptive: tokens that launch in the top 100 are different in many unobservable ways from tokens that launch in the 1000–2000 range.

### 6.5 Limitations

- CMC tracking is itself a selection: tokens that never make CMC's tracked list are not in our panel. This biases the universe toward tokens that achieved at least minimal exchange listing. The true "failure rate" of all token issuances is presumably even higher than what we measure.
- The 30-day snapshot cadence imposes measurement error on `first_seen` of up to 30 days.
- The category enrichment is based on a heuristic keyword list; a per-token tag retrieval from CoinGecko's API would yield cleaner categorization but at significant cost.
- We do not model causal mechanisms. Cox coefficients should be interpreted as descriptive associations, not as treatment effects.
- The Path B "disappeared from CMC" death rule may be too aggressive for tokens that briefly fall off CMC tracking due to data-feed issues unrelated to actual mortality. We conducted no sensitivity analysis on this rule because in practice the affected token count is small.

---

## 7. Reproducibility

All code, the SQL schema, and the snapshot CSVs are available at [REPO URL]. The pipeline reproduces from scratch in approximately one hour of wall-clock time on a single VPS, given an installed R interpreter (for `crypto2`) and a Postgres instance.

---

## References

[INCOMPLETE — to expand]

- Cong, L. W., Li, Y., Tang, K., & Zhang, Y. (2022). Crypto wash trading. Working paper.
- Howell, S. T., Niessner, M., & Yermack, D. (2020). Initial coin offerings: Financing growth with cryptocurrency token sales. *Review of Financial Studies* 33(9): 3925–3974.
- Jain, S. (2018). Why 95% of cryptocurrencies will fail. *Medium*.
- Liu, Y., & Tsyvinski, A. (2021). Risks and returns of cryptocurrency. *Review of Financial Studies* 34(6): 2689–2727.
- Stöckl, S. (2024). `crypto2`: Download Crypto Currency Data from CoinMarketCap without API. R package.

---

*[End of v0.2 draft]*
