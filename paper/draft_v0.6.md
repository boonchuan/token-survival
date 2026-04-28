# Token Mortality: A Survival Analysis of Cryptocurrency Cohorts, 2014–2024

**Boon Chuan Lim**
*Independent Researcher, Singapore*

**Draft v0.6 — April 28, 2026**

---

## Abstract

Across N=28,123 cryptocurrency tokens listed on CoinMarketCap between 2014 and 2024, we estimate empirical survival functions and document substantial heterogeneity by cohort and chain. Under a primary death definition that requires 180-day persistence at less than 1% of all-time-high price, less than \$1,000 daily volume, and absence from CMC's top-2,000 ranking, the unconditional 5-year survival rate is 17.0%, robust to alternative operationalizations (range 11.3% to 22.4% across four definitions). In contrast, a re-implementation of the simplified Feder et al. (2018) volume-only definition on our panel yields 83.0% mortality, illustrating definitional sensitivity and motivating our preference for compound multi-criterion definitions. The Weibull shape parameter is 1.37, indicating that baseline mortality hazard *increases* with token age — contrary to the common intuition that tokens which survive their first year are subsequently safer. Cox proportional hazards regression with cohort, chain, and launch-feature controls achieves a concordance index of 0.72. Initial market capitalization has economically negligible effects on survival, while initial trading volume (HR=0.94 per log unit) and initial CMC rank (HR=1.62 per log unit) are economically meaningful predictors. Tokens deployed on Ethereum exhibit lower mortality (42.0%) than those on Solana (49.0%) or Binance Smart Chain (47.7%); cohort effects dominate, with the 2014H2-2017H2 vintages showing 80-95% mortality and the 2021H2 cohort already at 79% by Q4 2024. The findings empirically refute the widely-cited "95% of cryptocurrencies will go to zero" claim as a short-to-medium term prediction — the unconditional rate is closer to 60% — while supporting it asymptotically: cohorts that have aged beyond five years show survival rates between 5% and 20%.

**JEL classification:** G12, G14, G32
**Keywords:** cryptocurrency, survival analysis, asset pricing, survivorship bias, token mortality

---

## 1. Introduction

The claim that "95% of cryptocurrencies will go to zero" is one of the most widely repeated maxims in digital asset markets. Its provenance traces to a 2018 *Medium* essay by Sowmay Jain that argued the long-run survival rate of crypto projects would mirror the survival rate of early-stage venture-backed startups. Eight years on, the qualitative claim has held up: across every major cohort since 2014, the majority of tokens listed during a peak speculative phase have lost almost all of their value within a few years. Yet the precise quantitative claim — the fraction that go to zero, the typical time to "death," the predictability of which tokens survive — remains incompletely characterized.

A small but active empirical literature has begun to address this question. Feder, Gandal, Hamrick, Moore, and Vasek (2018) and its extension Gandal et al. (2021) document abandonment dynamics in 1,082 coins and 725 tokens. Grobys and Sapkota (2020) examine 146 proof-of-work cryptocurrencies and find roughly 60% mortality. Fantazzini (2022, 2023) develops probability-of-death forecasting models on roughly 2,000 coins observed 2015–2020. Gatabazi, Mba, and Pindza (2022) apply Cox proportional hazards models to 500 cryptocurrencies through 2021. Section 2 reviews this literature in detail.

This paper extends the existing work in three respects. First, **scale**: we construct a survivorship-bias-free panel of 28,123 cryptocurrency tokens spanning 2014 to 2024 — roughly an order of magnitude larger than the largest comparable studies. Second, **methodological consolidation**: we apply standard survival-analysis tools (Kaplan-Meier estimation, Cox proportional hazards regression, Weibull accelerated failure time models) with a composite death definition combining price, volume, and ranking conditions, and report robustness across four alternative definitions. Third, **empirical refinement of the "95%" folklore**: we show that the popular claim is approximately correct at the cohort level for cohorts older than five years, but substantially overstates near-term mortality for younger cohorts.

The contribution is intentionally narrow. We do not attempt to identify the causal drivers of token death, predict future mortality, or model the macroeconomic determinants of cohort risk. Instead, we provide three things.

First, **a defensible operational definition of token death**. Existing work has typically relied on either single-condition definitions (volume drops below 1% of peak, after Feder et al. 2018) or exchange delistings, neither of which is fully satisfactory. We propose a primary definition combining three observable conditions — sustained low price relative to all-time-high, low trading volume, and exit from CMC's tracked-coin universe — and demonstrate that headline survival probabilities are robust across alternative definitions including a Feder-style price-only variant.

Second, **survival functions stratified by cohort and chain**. The cohort heterogeneity is dramatic: the 2014H2 cohort is 95.5% dead, the 2021H2 cohort is 78.8% dead despite being only three years old. Chain-level heterogeneity is also substantial and has not previously been documented at this resolution: tokens deployed on Ethereum exhibit lower mortality (42.0%) than those on Solana (49.0%) or Binance Smart Chain (47.7%), with native L1 coins surviving best of all (42.1% mortality, but with a markedly different long-tail shape).

Third, **a Cox regression of token mortality on launch-time observables**. The principal finding is that initial market capitalization has economically negligible effects on survival after cohort and chain controls; the strongest predictors are initial trading volume and initial rank.

A secondary finding deserves emphasis: **the Weibull shape parameter is well above unity** (k=1.37 under the primary definition, 1.13 to 1.77 across robustness variants). This implies that the conditional hazard of death is *increasing* in token age. Tokens that have survived their first three years are not safer than newly-launched tokens; if anything, their hazard rate is higher. This contradicts the common practitioner heuristic that "if a project survives the bear market it is fine."

The paper is structured as follows. Section 2 reviews the prior literature on cryptocurrency survival in detail. Section 3 describes the data construction. Section 4 specifies the death definitions and pre-registered statistical plan. Section 5 reports results. Section 6 discusses implications and limitations.

---

## 2. Related literature

A small but active empirical literature has emerged on the survival of cryptocurrency projects. We organize prior work into three strands and explain how this paper relates to each.

### 2.1 Coin abandonment and resurrection

The seminal contribution is Feder, Gandal, Hamrick, Moore, and Vasek (2018) — extended in Gandal, Hamrick, Moore, and Vasek (2021) — which develops a methodology for identifying coin "abandonment" and "resurrection" based on price and volume peaks. Studying 1,082 coins over a nearly five-year period, the original paper finds that 44% of publicly-traded coins are abandoned at least temporarily, 71% of abandoned coins are later resurrected, leaving 18% of coins to fail permanently. The extended 2021 version adds 725 tokens and finds tokens are abandoned less frequently than coins, with only 7% abandonment and 5% permanent token abandonment. Their definition — a drop in average daily trading volume to below 1% of a prior peak — became the canonical "Feder et al. (2018) criterion" used by subsequent work.

Our paper differs from Feder et al. in three respects. First, our sample is roughly 17 times larger (28,123 versus 1,807 coins+tokens) and extends six additional years through 2024, capturing the post-ICO regulatory regime, the DeFi summer of 2020, the NFT/memecoin boom of 2021, and the bear-market fallout of 2022–2023. Second, we apply formal survival-analysis machinery (Kaplan-Meier estimation, Cox PH regression, Weibull AFT) rather than abandonment indicators, allowing proper handling of right-censoring. Third, our composite death definition combines price, volume, and ranking conditions, which we argue is more defensible than any single-condition definition; we report robustness across four variants including a Feder-inspired price-only variant.

### 2.2 Probability-of-death modelling

A second strand treats token death as a credit-risk event and develops forecasting models. Grobys and Sapkota (2020) examined 146 proof-of-work cryptocurrencies trading before 2015 and followed them through December 2018, finding that about 60% of those cryptocurrencies died, and employing linear discriminant analysis to forecast defaults — though their model could predict most cryptocurrency bankruptcies but not the cryptocurrencies that remained alive. Fantazzini and Zimin (2020) formalize the credit-risk framing for cryptocurrencies and propose the zero-price-probability (ZPP) approach. Fantazzini (2022) extends this to over two thousand crypto-coins observed between 2015 and 2020, comparing credit-scoring models, machine learning, and time-series-based methods across multiple death definitions, finding that cauchit and ZPP-based models perform best for newly-established coins while credit-scoring and machine-learning methods using lagged volumes and online searches are better for older coins. Fantazzini (2023) extends the same methodology using daily-range volatility models. Most recently, Fantazzini (2025) applies panel binary models to stablecoin failure.

This strand is concerned primarily with *forecasting* individual-coin failure for risk-management purposes. Our contribution is complementary and orthogonal: we focus on the *empirical survival function* of the population — characterizing what mortality looks like across cohorts and chains rather than predicting which specific coins will die next.

### 2.3 Cox-regression studies of crypto survival

Closest in method to our paper is Gatabazi, Mba, and Pindza (2022), who apply Cox proportional hazards and Aalen additive hazards models to cryptocurrency survival from 2009 to 2021. They use six covariates of interest, finding that cryptocurrencies under standalone blockchain were at relatively higher risk of collapsing, that the 2013–2017 release cohort was at higher risk than the 2009–2013 release, and that cryptocurrencies for which headquarters are known had relatively better survival outcomes. Their sample is constrained to 500 cryptocurrencies for which white-paper-level information is available. We extend this approach to the full CoinMarketCap-tracked universe (28,123 tokens), three years of additional data, and chain-of-deployment as a primary covariate.

### 2.4 Adjacent literature on cryptocurrency markets

Howell, Niessner, and Yermack (2020) study initial coin offerings as a financing mechanism and document poor outcomes for the median ICO project. Liu and Tsyvinski (2021) characterize cryptocurrency returns at the asset-class level. Gandal, Hamrick, Moore, and Oberman (2018) document price manipulation in Bitcoin markets, and Gandal, Hamrick, Rouhi, Mukherjee, Feder, Moore, and Vasek (2021) document pump-and-dump schemes — both of which are relevant context for understanding the population from which dead coins are drawn but are methodologically distinct from survival analysis.

### 2.5 Our contribution in the literature

Our paper makes three contributions relative to the existing body of work. First, **scale**: at 28,123 tokens spanning eleven years, our sample is roughly an order of magnitude larger than the largest comparable studies and includes the full universe of CMC-tracked tokens rather than a curated subset. Second, **methodological consolidation**: we combine the Feder-style death definition with formal survival analysis, retain the Fantazzini-style robustness across multiple death criteria, and add chain-level heterogeneity not previously documented. Third, **empirical refinement of the "95%" folklore claim**: we show that the popular claim is approximately correct at the cohort level for cohorts older than five years (80–95% mortality), but substantially overstates near-term mortality for younger cohorts. This nuance has not previously been quantified.

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
- `category`: heuristic classification from a curated keyword list applied to token name and symbol, in {stablecoin, meme, DeFi, gaming, other}
- `cohort_half`: calendar half-year of first appearance

The CG-based chain assignment matches 12,609 of 28,123 tokens (44.8%); the remaining 55.2% are classified as `unknown`. This match rate has two implications worth flagging upfront. First, the `unknown` group is not random — it is heavily weighted toward small-cap and dead tokens that never made it into CG's index, and we treat it as its own category in all chain analyses. Second, our chain-conditional results are based on the matched subset and should be interpreted accordingly; we report the unmatched group's mortality alongside the matched groups in Section 5.4 for transparency. The category classification is intentionally simple — based on a curated keyword list — and we acknowledge it is materially noisier than per-token tag retrieval would be. We treat category as an exploratory rather than a primary covariate, and discuss the implications in Section 6.

We deliberately exclude richer covariates (GitHub activity, Twitter follower trajectories, on-chain TVL, audit status) from this version of the paper. Their construction at scale across the full 2014–2024 universe is prohibitively expensive and would mostly substitute correlation for prediction.

---

## 4. Death definitions and statistical plan

### 4.1 Primary death definition

The most widely cited prior definition is that of Feder, Gandal, Hamrick, Moore, and Vasek (2018), simplified by Schmitz and Hoffmann (2020): a coin is "abandoned" if its average daily trading volume for a given month is at most 1% of its all-time peak monthly volume, with "resurrection" declared if volume subsequently recovers to at least 10% of peak. Fantazzini (2022) and subsequent work in the credit-risk strand build on variants of this definition.

We adopt a more comprehensive definition for three reasons. First, **the volume-only condition is vulnerable to non-organic volume**, including wash trading and pump-and-dump activity (documented at scale by Cong, Li, Tang, and Zhang 2022 and Gandal, Hamrick, Rouhi, Mukherjee, Feder, Moore, and Vasek 2021). A token can be effectively dead but generate brief volume spikes that disqualify it from a volume-only "dead" classification. Adding a price condition (price ≤ 1% of all-time-high) requires that the token be both illiquid *and* priced near zero, making manipulation-driven false-negatives less likely. Second, **a single-month observation window is fragile**: a token might briefly fall below the threshold during a market event and recover within weeks. Our 180-day window forces sustained inactivity before death is declared. Third, **CMC's tracked-coin universe (top-2,000) is itself an informative signal**: tokens that fall out of CMC's tracked list have effectively lost both exchange listings and analyst attention, which is a more durable form of mortality than volume alone would capture.

The primary definition is therefore: a token is declared dead at observation date *t* if all of the following hold for the 180 consecutive days ending at *t*:

1. Price ≤ 1% of all-time-high USD price
2. 24-hour trading volume < \$1,000
3. CMC rank > 2,000 (or absent from CMC tracking entirely)

Death is recorded at the earliest such *t*. Tokens that never satisfy these conditions by 2024-12-04 are right-censored at that date. We require at least two observations within the 180-day window for an in-panel death event to be declared, eliminating spurious deaths from isolated bad data points.

A token whose `last_obs` precedes the end of the study period by at least the window length and which never reappears is also declared dead (death date assigned at `last_obs + window_days`). This captures the common case where a token is dropped from CMC tracking entirely after losing exchange listings — the rank condition is satisfied vacuously, and the price/volume conditions are unobservable but, in practice, near-uniformly satisfied. We discuss this rule's heavy contribution to total declared deaths (approximately 85% of the primary-definition deaths) in Sections 5.8 and 6.5.

A reasonable alternative would be a disjunctive (OR) rule: declare death if any one of price, volume, or rank conditions holds. We deliberately choose the conjunctive (AND) rule to minimize false positives. A token that retains a price above 1% of all-time-high, even with minimal volume, may still be considered alive by some market participants — the asset has not yet collapsed in the price dimension. Our goal is to identify durable, unambiguous death rather than transient illiquidity. We acknowledge this choice trades off some true positives (tokens that are dead by any reasonable standard but happen to retain one healthy condition) for fewer false positives; Section 5.8 reports the consequences of this trade-off via direct comparison with the Feder volume-only definition.

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

Figure 1 plots the Kaplan-Meier survival function under the primary definition, with 95% confidence band. Headline survival probabilities at 1, 3, and 5 years from listing are presented in Table 2, alongside the same statistics under the three robustness variants:

| Definition  | S(1y)  | S(3y)  | S(5y)  |
|-------------|--------|--------|--------|
| primary     | 67.9%  | 30.2%  | 17.0%  |
| loose       | 58.2%  | 26.2%  | 14.6%  |
| strict      | 94.7%  | 38.0%  | 22.4%  |
| price_only  | 62.5%  | 23.0%  | 11.3%  |

Five years is the most natural benchmark horizon. **Five-year survival is 17.0% under the primary definition, with bounds of approximately [11%, 22%] across alternative operationalizations.** Beyond the five-year mark, the curve flattens slowly: 7-year survival is approximately 10%, and tokens that have survived eleven years (the 2014 cohort) show 5-year-conditional survival near zero — that is, almost no token from 2014 that was alive in 2019 remains alive today.

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

### 5.4 Heterogeneity by chain

Table 4 reports the proportion of tokens dead under the primary definition by chain assignment, and Figure 3 plots the corresponding survival functions:

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

Tokens whose chain CG could not assign (`unknown`) have 75% mortality, reflecting the strong selection effect: if a token is not in CG's index, it is disproportionately likely to be dead or never to have traded meaningfully. Among tokens with a confidently-assigned chain, **Ethereum-deployed tokens have the lowest mortality (42.0%)**, followed by native L1 coins (42.1%), and tokens on Tron (37.7%, dominated by stablecoin issuance via TRC-20). Tokens deployed on Solana (49.0%) and Binance Smart Chain (47.7%) — the chains most associated with the 2021 memecoin and high-throughput DEX boom — exhibit roughly 7 percentage points higher mortality than Ethereum.

Figure 3 reveals two structural patterns not visible in the cumulative table. First, **native L1 coins (n=556) are dramatically the best long-run survivors**, plateauing near 36% survival at 11 years against under 15% for any smart-contract platform. This is partly mechanical: a chain's own coin cannot be delisted from CMC because the chain anchors the listing, and chains themselves have higher persistence than the dApps they host. Second, **Ethereum's higher survival relative to Solana and BSC is concentrated in the early years** (days 0–1500); the curves converge somewhat in the long tail, reaching similar 8-year levels in the 8–15% range. We do not interpret this gap causally — chain-of-deployment is correlated with launch-time liquidity, deployment cost, and project type, all of which independently affect survival.

The log-rank test for chain effects is highly significant (p effectively zero at machine precision).

### 5.5 Cox regression

Table 5 presents Cox proportional hazards estimates under the primary definition. The model includes log initial market cap, log initial volume, log initial rank, chain dummies, category dummies, and cohort half dummies. The concordance index is 0.722, comparable to standard credit-risk and corporate-default models in the empirical finance literature — moderate predictive power but well short of deterministic.

Selected coefficients (full table in supplementary materials):

| Covariate                  | exp(coef) | 95% CI         | p           |
|----------------------------|-----------|----------------|-------------|
| log_initial_mcap_usd       | 1.007     | [1.001, 1.012] | 0.026       |
| log_initial_volume_usd     | 0.941     | [0.937, 0.945] | < 10^-100   |
| log_initial_rank           | 1.621     | [1.552, 1.693] | < 10^-100   |
| cohort_half_2020H1 (vs 2014H1) | 0.377 | [0.324, 0.438] | < 10^-30    |
| cohort_half_2021H2 (vs 2014H1) | 0.752 | [0.666, 0.849] | < 10^-5     |

**Initial market capitalization has economically negligible effects.** The estimated hazard ratio is 1.007 per log unit of market cap, meaning that even a 1000x difference in launch market cap changes hazard by only roughly 5%. This is statistically significant (p=0.026) but practically meaningless. The intuition that "tokens with bigger launches survive better" is not supported once volume and rank are controlled for.

**Initial trading volume is the strongest economically-meaningful predictor among continuous launch-time variables.** A 10x increase in initial volume is associated with a 14% reduction in hazard (HR = 0.941^log(10) ≈ 0.86). Volume captures market interest in a way that market cap, which is largely determined by token economics rather than market depth, does not.

**Initial CMC rank has the largest single effect.** A 10x increase in rank number (i.e., dropping from rank 100 to rank 1000) raises hazard by 62%. We caution that rank, volume, and market cap are non-trivially collinear at launch, and the 1.62 HR likely absorbs information about liquidity and exchange coverage that the other variables cannot fully capture. A specification that drops rank yields qualitatively similar findings on the other coefficients but a substantial drop in concordance, consistent with rank acting as a near-sufficient statistic for launch-time market quality.

**Cohort effects are large and non-monotonic.** Relative to the 2014H1 reference cohort, the 2018H1, 2019, and 2020H1 cohorts show substantially lower hazard (HR ≈ 0.38–0.51) — these are the cohorts that benefited from the 2020-2021 bull market having time to validate the strongest projects. The 2021H2 cohort's HR of 0.75 is closer to the 2014H1 baseline, reflecting the elevated speculative excess of that period.

### 5.6 Weibull shape

The Weibull AFT model yields shape parameters as follows:

| Definition  | k    |
|-------------|------|
| primary     | 1.37 |
| loose       | 1.13 |
| strict      | 1.77 |
| price_only  | 1.39 |

**All four definitions give k > 1, indicating that the baseline hazard increases with token age.** This is a meaningful empirical contradiction of the practitioner intuition that surviving the first year confers safety. Possible mechanisms include: (a) tokens that survive the first wave of attention but never achieve organic adoption fade gradually rather than abruptly; (b) protocol obsolescence as newer technologies displace older ones; (c) team attrition as developer focus moves to new projects.

We urge interpretive caution. The Weibull shape parameter describes the *baseline* hazard under the assumption of proportional hazards — that is, the hazard for a token with average covariate values, abstracting from individual token heterogeneity. Unobserved heterogeneity in token quality, founder commitment, or protocol value can bias the estimated shape parameter upward: if good tokens never die and bad tokens die early, the residual population at later horizons is increasingly composed of intermediate-quality tokens, which can produce an apparent increase in baseline hazard even if no individual token's hazard is rising. The increasing-hazard finding should therefore be viewed as suggestive of a population-level pattern rather than as a definitive claim about individual token risk dynamics.

The shape parameter under the strict (365-day) definition is the highest (k=1.77), because requiring a longer period of zero activity excludes tokens that might briefly recover. Under the loose (90-day) definition, k=1.13 is closer to constant hazard, capturing more rapid early deaths.

### 5.7 Robustness

Headline survival probabilities and Cox concordance indices across all four death definitions are summarized in Table 6 (`summary_table.csv` in the supplementary materials). The qualitative findings hold across all variants: 5-year survival between 11% and 22%, Weibull k > 1, Cox concordance 0.69–0.72, log-rank cohort effects highly significant in every case.

### 5.8 Comparison with prior survival estimates

To anchor our results in the existing literature, we re-implemented the simplified Feder et al. (2018) / Schmitz and Hoffmann (2020) volume-only definition on our panel. A token is declared dead at observation *t* if its volume falls to ≤ 1% of all-time peak volume at any point, with resurrection if volume subsequently recovers to ≥ 10% of peak. We adopt the same Path B disappearance rule (90-day window) for consistency with the other definitions reported in this paper.

Under the Feder simplified definition applied to our panel, **23,331 of 28,123 tokens (83.0%) are classified as dead**, substantially higher than our primary definition's 61.5%. This is initially counterintuitive but reflects the structural difference between the definitions:

- The Feder definition declares death the *moment* volume crosses below the threshold, even instantaneously. Our primary definition requires the death conditions to hold for 180 consecutive days.
- The Feder definition uses volume alone. Our primary definition requires concurrent failure on price (≤ 1% of ATH), volume, and CMC rank.

Our primary definition is therefore more conservative — slower to declare death and more demanding about what death entails. The fact that 21.5 percentage points of tokens are "dead" under Feder but "alive" under our definition reflects tokens that have experienced a single-period volume collapse but recovered, retain meaningful price, or remain in the top-2,000 ranked universe. Whether to classify such tokens as dead is a methodological choice; our preference for the stricter definition follows from the goal of identifying *durable* mortality rather than transient illiquidity.

Reconciliation with prior reported numbers:

- **Feder et al. (2018)** report 44% of coins "abandoned at least temporarily" with 71% resurrection, implying 18% permanent abandonment in their 1,082-coin sample (2013–2018). Our 83% Feder re-implementation is not directly comparable to their 18% permanent abandonment figure: we apply the same volume-only rule but over a much longer observation window (eleven years versus five), with a sample 26 times larger, and we treat Path B disappearance from CMC tracking as a death event. The substantially higher number is consistent with mortality rates rising with follow-up time and with the inclusion of post-2018 cohorts that postdate Feder's study. The most direct comparable figure — the Feder rate restricted to comparable cohorts — would require restricting our sample to pre-2018 listings; we leave that finer-grained reconciliation to future work.

- **Grobys and Sapkota (2020)** find ~60% mortality on 146 PoW coins through December 2018. Our primary definition (61.5%) is essentially identical in central tendency, despite using a different definition and a much larger and more recent sample.

- **Gandal et al. (2021)** report 7% temporary abandonment and 5% permanent abandonment for 725 tokens. This is dramatically lower than any of our estimates, reflecting their very different sample (the small set of token-class assets that existed and were tracked pre-2018).

The substantive point is that headline mortality rates are sensitive to the specific definition, sample period, and resurrection accounting. Reporting multiple definitions — as we do across our four primary variants plus the Feder re-implementation — is the appropriate response to a literature in which no canonical definition exists. The 5-year survival probabilities we report (between 11% and 22% depending on definition) and the cohort-conditional rates (80–95% for cohorts older than five years) are the more robust quantities, since they depend less on the precise threshold and more on the underlying age-mortality relationship.

---

## 6. Discussion

### 6.1 Reconsidering "95% will go to zero"

The folklore claim that 95% of cryptocurrencies will go to zero is approximately right at the cohort level for any cohort older than five years, and approximately right asymptotically for the entire sample, but it is misleading as an unconditional claim about "current" tokens. At any given moment, the unconditional dead-rate in the population is bounded by the cohort-mix: in a market with rapid new-token issuance (as in 2021–2024), the unconditional rate looks lower because newer cohorts have not had time to die. Investors interpreting "95% will go to zero" as a near-term forecast are extrapolating a long-run cohort property to a short-run population property, which is not warranted.

A more accurate restatement is: *for cohorts that have had five years to mature, mortality is between 80% and 95%; this rate is converging downward across cohorts as median project quality improves, but only modestly.* The 2018-2020 cohorts that arose in the post-ICO regulatory tightening have somewhat better survival than the pure-ICO 2014–2017 cohorts, but the difference is in the range of 10–20 percentage points, not 50.

### 6.2 The increasing-hazard finding

The Weibull shape parameter exceeding unity is a result that we did not anticipate ex ante and that warrants future investigation. The conventional view, articulated by venture capitalists and crypto practitioners alike, is that early failure dominates: most projects die in the first 12 months, and survivors are progressively safer. Our data does not support this. Tokens that have survived three or four years face higher conditional hazard than newly-launched tokens.

We caution that this result may partly reflect the construction of our death definition rather than an inherent feature of crypto asset failure. Newly-launched tokens have less opportunity to accumulate the 180-day "in death state" run required by our definition; they may be effectively dead but censored by the requirement that they have first been alive long enough to die. A more granular analysis using continuous time-varying risk would illuminate this further.

### 6.3 Chain-conditional mortality

Tokens deployed on Ethereum show 7 percentage points lower mortality than those on Solana or Binance Smart Chain. We are deliberately cautious about the interpretation. Several mechanisms could produce this association without any direct causal effect of chain choice — stronger developer ecosystems supporting projects through downturns, deeper DEX liquidity providing baseline trading, lower-quality projects being self-selected to chains with cheaper deployment costs. Our descriptive estimate is the joint association; disentangling these mechanisms is left to future work with more granular data on project quality at launch.

### 6.4 What the regression does and does not imply

The Cox regression should be interpreted as a descriptive characterization of the joint distribution of survival and observable features at launch, not as a treatment-effect identification. The result that initial market cap has near-zero effect after controlling for volume and rank does not mean that "raising more capital does not help projects survive"; it likely means that initial market cap is not a sufficient statistic for the project quality that matters for survival, after controlling for the variables that are. The strong rank effect is similarly descriptive: tokens that launch in the top 100 are different in many unobservable ways from tokens that launch in the 1000–2000 range.

### 6.5 Limitations

- CMC tracking is itself a selection: tokens that never make CMC's tracked list are not in our panel. This biases the universe toward tokens that achieved at least minimal exchange listing. The true "failure rate" of all token issuances is presumably even higher than what we measure.
- The 30-day snapshot cadence imposes measurement error on `first_seen` of up to 30 days.
- The category enrichment is based on a heuristic keyword list; a per-token tag retrieval from CoinGecko's API would yield cleaner categorization but at significant cost.
- We do not model causal mechanisms. Cox coefficients should be interpreted as descriptive associations, not as treatment effects.
- The "disappearance from CMC tracking" rule for declaring death (the second branch of the death definition described in Section 4.1) is the methodologically most contestable choice in the paper. Approximately 85% of declared deaths under the primary definition derive from this branch rather than from in-panel observation of bad readings. The defensive case is that disappearance from CMC tracking is itself a defensible mortality signal — a token that has lost all its exchange listings *is* effectively dead from the perspective of any investor — but a sensitivity analysis restricting attention to in-panel deaths would be a useful extension. We anticipate this in v2.

---

## 7. Reproducibility

All code, the SQL schema, and the snapshot CSVs are available from the author upon request and will be hosted at a public repository (GitHub with Zenodo DOI) prior to journal submission. The pipeline reproduces from scratch in approximately one hour of wall-clock time on a single VPS, given an installed R interpreter (for `crypto2`) and a Postgres instance.

---

## Figures

- **Figure 1.** Pooled Kaplan-Meier survival function, primary definition. 95% CI band. Source: `data/results/km_pooled_primary.png`.
- **Figure 2.** Kaplan-Meier survival functions stratified by cohort half-year, primary definition. Eight largest cohorts shown for legibility. Source: `data/results/km_by_cohort_half_primary.png`.
- **Figure 3.** Kaplan-Meier survival functions stratified by chain assignment, primary definition. Source: `data/results/km_by_chain_primary.png`.

Equivalent figures under the three alternative death definitions are provided in supplementary materials.

---

## References

Cong, L. W., Li, Y., Tang, K., & Zhang, Y. (2022). Crypto wash trading. NBER Working Paper 30783.

Fantazzini, D. (2019). *Quantitative finance with R and cryptocurrencies*. Amazon KDP. ISBN 978-1090685315.

Fantazzini, D. (2022). Crypto-coins and credit risk: Modelling and forecasting their probability of death. *Journal of Risk and Financial Management*, 15(7), 304. https://doi.org/10.3390/jrfm15070304

Fantazzini, D. (2023). Assessing the credit risk of crypto-assets using daily range volatility models. *Information*, 14(5), 254. https://doi.org/10.3390/info14050254

Fantazzini, D. (2025). Detecting stablecoin failure with simple thresholds and panel binary models: The pivotal role of lagged market capitalization and volatility. *Forecasting*, 7(4), 68.

Fantazzini, D., & Zimin, S. (2020). A multivariate approach for the simultaneous modelling of market risk and credit risk for cryptocurrencies. *Journal of Industrial and Business Economics*, 47, 19–69.

Feder, A., Gandal, N., Hamrick, J. T., Moore, T., & Vasek, M. (2018). The rise and fall of cryptocurrencies. In *Proceedings of the 17th Workshop on the Economics of Information Security (WEIS)*, Innsbruck, Austria.

Gandal, N., Hamrick, J. T., Moore, T., & Oberman, T. (2018). Price manipulation in the Bitcoin ecosystem. *Journal of Monetary Economics*, 95, 86–96.

Gandal, N., Hamrick, J. T., Moore, T., & Vasek, M. (2021). The rise and fall of cryptocurrency coins and tokens. *Decisions in Economics and Finance*, 44(2), 981–1014. https://doi.org/10.1007/s10203-021-00329-8

Gatabazi, P., Mba, J. C., & Pindza, E. (2022). Cryptocurrencies and tokens lifetime analysis from 2009 to 2021. *Economies*, 10(3), 60. https://doi.org/10.3390/economies10030060

Grobys, K., & Sapkota, N. (2020). Predicting cryptocurrency defaults. *Applied Economics*, 52(46), 5060–5076. https://doi.org/10.1080/00036846.2020.1752903

Howell, S. T., Niessner, M., & Yermack, D. (2020). Initial coin offerings: Financing growth with cryptocurrency token sales. *Review of Financial Studies*, 33(9), 3925–3974.

Jain, S. (2018). Why 95% of cryptocurrencies will fail. *Medium*.

Liu, Y., & Tsyvinski, A. (2021). Risks and returns of cryptocurrency. *Review of Financial Studies*, 34(6), 2689–2727.

Schmitz, T., & Hoffmann, I. (2020). Re-evaluating cryptocurrencies' contribution to portfolio diversification — A portfolio analysis with special focus on German investors. arXiv preprint arXiv:2006.06237.

Stöckl, S. (2024). `crypto2`: Download cryptocurrency data from CoinMarketCap without API. R package, version 2.x. https://github.com/sstoeckl/crypto2

---

*[End of v0.6 draft]*
