import os
import sys

import pandas as pd

from config import LEGACY_CIKS
from src.data.edgar_client import cik_lookup, fetch_form4_index, fetch_form4_xml
from src.data.form4_parser import parse_form4_xml

TICKER = sys.argv[1]
START_DATE = "2016-01-01"
OUTPUT_PATH = "data/raw/form4_transactions.csv"

cik10 = cik_lookup([TICKER])[TICKER]
ciks_to_pull = [cik10] + LEGACY_CIKS.get(TICKER, [])

rows = []
for cik in ciks_to_pull:
    filings = fetch_form4_index(cik)
    filings = filings[filings["filingDate"] >= START_DATE]
    print(f"{TICKER} (CIK {cik}): {len(filings)} Form 4 filings since {START_DATE}")

    for i, (_, filing) in enumerate(filings.iterrows(), start=1):
        if i % 20 == 0:
            print(f"  ...{TICKER} progress: {i}/{len(filings)} filings processed")
        try:
            xml_bytes = fetch_form4_xml(cik, filing["accessionNumber"], filing["primaryDocument"])
            rows.extend(parse_form4_xml(xml_bytes, filing["accessionNumber"]))
        except Exception as e:
            print(f"Skipped {TICKER} {filing['accessionNumber']}: {e}")

ticker_df = pd.DataFrame(rows)
if not ticker_df.empty:
    ticker_df = ticker_df[ticker_df["ticker"] == TICKER]

write_header = not os.path.exists(OUTPUT_PATH)
ticker_df.to_csv(OUTPUT_PATH, mode="a", header=write_header, index=False)
print(f"Appended {len(ticker_df)} rows for {TICKER} to {OUTPUT_PATH}")