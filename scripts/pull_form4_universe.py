import os

import pandas as pd

from config import LEGACY_CIKS, TICKERS
from src.data.edgar_client import cik_lookup, fetch_form4_index, fetch_form4_xml
from src.data.form4_parser import parse_form4_xml

START_DATE = "2016-01-01"
OUTPUT_PATH = "data/raw/form4_transactions.csv"

if os.path.exists(OUTPUT_PATH):
    os.remove(OUTPUT_PATH)

cik_map = cik_lookup(TICKERS)
missing = set(TICKERS) - cik_map.keys()
if missing:
    print(f"No CIK found for: {sorted(missing)}")

for ticker, cik10 in cik_map.items():
    ciks_to_pull = [cik10] + LEGACY_CIKS.get(ticker, [])
    rows = []

    for cik in ciks_to_pull:
        filings = fetch_form4_index(cik)
        filings = filings[filings["filingDate"] >= START_DATE]
        print(f"{ticker} (CIK {cik}): {len(filings)} Form 4 filings since {START_DATE}")

        for _, filing in filings.iterrows():
            try:
                xml_bytes = fetch_form4_xml(cik, filing["accessionNumber"], filing["primaryDocument"])
                rows.extend(parse_form4_xml(xml_bytes, filing["accessionNumber"]))
            except Exception as e:
                print(f"Skipped {ticker} {filing['accessionNumber']}: {e}")

    ticker_df = pd.DataFrame(rows)
    if not ticker_df.empty:
        ticker_df = ticker_df[ticker_df["ticker"].isin(TICKERS)]

    write_header = not os.path.exists(OUTPUT_PATH)
    ticker_df.to_csv(OUTPUT_PATH, mode="a", header=write_header, index=False)
    print(f"Appended {len(ticker_df)} rows for {ticker} to {OUTPUT_PATH}")

print(f"Done. Full dataset saved incrementally to {OUTPUT_PATH}")