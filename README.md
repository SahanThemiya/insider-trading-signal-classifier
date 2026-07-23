# Insider Trading Signal Classifier

Classifies corporate insider stock trades (SEC Form 4) into Routine, Noise, and
Opportunistic categories using forward Cumulative Abnormal Return (CAR) labeling
and engineered trade/market features.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then fill in your Alpaca keys
```

Alpaca paper trading keys (free) work fine for historical market data — get them at
https://alpaca.markets.

## Project layout

```
src/data/
    trading_calendar.py   NYSE trading-day alignment (weekends, holidays)
    alpaca_client.py      Split/dividend-adjusted daily bar retrieval
scripts/
    pull_and_align_demo.py  End-to-end example: trade date -> aligned bars
tests/
    test_trading_calendar.py
data/raw/                Raw Form 4 + Alpaca pulls (gitignored)
data/processed/          Labeled, feature-engineered datasets (gitignored)
```

## Run the demo

```bash
python -m scripts.pull_and_align_demo
```

## Run tests

```bash
pytest
```
