# Insider Trading Signal Classifier

Classifies corporate insider stock trades (SEC Form 4) into three categories — Routine, Noise, and Opportunistic — using a two-stage rule-based and statistical labeling methodology, then evaluates whether machine learning models can distinguish genuinely informative trades from noise.

## Motivation

Real, illegal insider trading is far too rare to train a classifier directly on. This project instead defines "Opportunistic" trades using a statistical proxy: unscheduled trades followed by abnormally large, direction-consistent price moves relative to the broader market. This produces a populated, learnable target while staying grounded in real regulatory filings and real market data, not invented labels.

## Methodology

### Stage A — Rule-based labeling (Routine)

Trades executed under a Rule 10b5-1 trading plan are labeled Routine (Class 0) regardless of what the stock does afterward, since the trade decision was locked in before any market-moving information could have existed. Detected via SEC's `aff10b5One` filing flag (added 2023), with a footnote-text fallback for older filings.

### Stage B — Statistical labeling (Noise vs. Opportunistic)

For all remaining discretionary open-market trades (buy/sell only — grants, gifts, and option exercises are excluded as non-discretionary):

1. Compute 30-day forward Cumulative Abnormal Return (CAR): the stock's return minus the S&P 500's return over the same trading-day window.
2. Derive Class 1/2 thresholds from the empirical CAR distribution (15th/85th percentile) rather than fixed, arbitrary cutoffs.
3. Apply a direction-consistency rule: a buy only counts as Opportunistic if followed by abnormally positive CAR, a sell only counts if followed by abnormally negative CAR. A sell before a rally, or a buy before a crash, is Noise regardless of magnitude.

### Feature engineering

- **Ownership change %** — this trade's size relative to the insider's total position
- **Trade size intensity** — this trade's dollar value vs. that insider's own historical median (leakage-safe: uses only prior trades)
- **Insider clustering** — count of other insiders at the same company trading in the trailing 7 days
- **Pre-trade volatility** — 14-day trailing volatility, excluding the trade date itself

### Modeling

Only Class 1 vs. Class 2 is modeled, since Class 0 is fully solved by the rule. Logistic Regression (baseline) and XGBoost (primary candidate) are compared using a chronological train/test split, not a random shuffle, to avoid look-ahead bias, with precision/recall analyzed across thresholds rather than a default 0.5 cutoff.

## Data sources

- **SEC EDGAR** — Form 4 filings parsed directly from raw XML, not scraped from third-party aggregators, to respect SEC's fair-access policy.
- **Alpaca Markets** — daily OHLCV bars, split/dividend-adjusted, for target tickers and the SPY benchmark.

## Ticker universe

XOM, CVX, COP, MPC, LMT, RTX, PLTR, LDOS, UAL, FDX, DAL — spanning energy, defense, and airlines, chosen for geopolitical and fuel-price exposure relevant to 2025-2026 market conditions. Data covers 2016-2026.

## Results

| Metric (Opportunistic class, default threshold) | 342 trades (2023-2026) | 1,221 trades (2016-2026) |
|---|---|---|
| Logistic Regression — precision / recall | 0.12 / 0.50 | 0.11 / 0.38 |
| XGBoost — precision / recall | 0.00 / 0.00 | 0.14 / 0.52 |

Scaling the real dataset roughly 7x, by extending the date range on the same 11 tickers, measurably improved XGBoost: from finding zero true positives to correctly catching over half of real Opportunistic trades, with precision modestly above the ~13% base rate. At stricter thresholds (0.65-0.75) precision rises further to 0.15-0.18, though the sample sizes there (6-17 flagged trades) are too small to treat as conclusive on their own. Logistic Regression showed no improvement, consistent with a weak, nonlinear signal rather than a simple linear one.

**Honest interpretation:** this is early evidence of a weak but real signal, not a validated strong classifier. CAR-based labels are a statistical proxy, not verified ground truth — some fraction of "Opportunistic" labels are almost certainly coincidental price moves unrelated to genuine informed trading. This creates a real ceiling on achievable precision, and is a known, documented limitation of this research approach in general, not a flaw specific to this pipeline.

## Synthetic data (pipeline validation only)

`scripts/generate_synthetic_data.py` generates a large synthetic dataset with a designed, known signal-to-noise ratio. Its only purpose is confirming the modeling pipeline (feature handling, imputation, chronological splitting, threshold tuning) correctly learns real patterns given adequate sample size. It is never used as, or mixed with, the project's actual reported results. On synthetic data, both models recover the designed signal cleanly (precision climbing from ~0.14 to ~0.74 as the threshold tightens), confirming the modest real-data results above reflect genuine data characteristics rather than a broken pipeline.

## Project layout
```
insider-trading-signal-classifier/ 
├── config.py API keys, ticker universe, legacy CIK mapping
├── requirements.txt
├── pytest.ini
├── .env.example
├── data/
│ ├── raw/ Form 4 pulls (gitignored)
│ ├── processed/ Labeled data, engineered features (gitignored)
│ └── synthetic/ Pipeline validation data only (gitignored)
├── src/
│ ├── data/
│ │ ├── trading_calendar.py NYSE trading-day alignment
│ │ ├── alpaca_client.py Split/dividend-adjusted price retrieval
│ │ ├── edgar_client.py CIK lookup, filing index, XML fetch
│ │ └── form4_parser.py Form 4 XML parsing, 10b5-1 detection
│ ├── labeling/
│ │ ├── car.py Cumulative abnormal return calculation
│ │ ├── label_transactions.py Class 0/1/2 labeling rules
│ │ └── aggregate_filings.py Multi-tranche and ownership-nature aggregation
│ ├── features/
│ │ └── build_features.py Feature engineering functions
│ └── modeling/
│ └── prepare_dataset.py Stage B prep, imputation, chronological split
├── scripts/ Orchestration entry points
└── tests/ 25 tests covering every pipeline stage
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # fill in Alpaca keys and SEC_USER_AGENT
```

## Running the pipeline

```bash
python -m scripts.pull_form4_universe      # Pull Form 4 filings for the ticker universe
python -m scripts.label_transactions       # Compute CAR and apply labeling rules
python -m scripts.build_features           # Engineer features
python -m scripts.train_model              # Train and evaluate both models
```

`scripts/pull_single_ticker.py <TICKER>` re-pulls a single ticker without re-running the full universe. `scripts/pull_and_align_demo.py` is a quick smoke test of the price-alignment logic.

## Tests

```bash
pytest -q
```

## Known limitations and future work

- CAR-based labels are a statistical proxy for informed trading, not verified ground truth.
- 10b5-1 detection before 2023 relies on footnote-text matching rather than SEC's explicit flag.
- The ticker universe (11 companies) limits total sample size; expanding within the energy/defense/airline sector, or extending the date range further, are the clearest levers for more data.
- Congressional/political trading disclosures were evaluated as a data source and ruled out: they use dollar-range reporting rather than exact share counts, breaking several existing features, and would likely yield fewer matching trades than the current universe, not more.

## Tools

Python, pandas, NumPy, scikit-learn, XGBoost, lxml, SEC EDGAR API, Alpaca Markets API, pytest.
