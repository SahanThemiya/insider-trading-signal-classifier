import pandas as pd

from config import LEGACY_CIKS, TICKERS
from src.data.edgar_client import cik_lookup, fetch_form4_index, fetch_form4_xml
from src.data.form4_parser import parse_form4_xml

START_DATE = "2023-01-01"
OUTPUT_PATH = "data/raw/form4_transactions.csv"

cik_map = cik_lookup(TICKERS)
missing = set(TICKERS) - cik_map.keys()
if missing:
    print(f"No CIK found for: {sorted(missing)}")

rows = []
for ticker, cik10 in cik_map.items():
    ciks_to_pull = [cik10] + LEGACY_CIKS.get(ticker, [])

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

transactions = pd.DataFrame(rows)
transactions = transactions[transactions["ticker"].isin(TICKERS)]
transactions.to_csv(OUTPUT_PATH, index=False)
print(f"Saved {len(transactions)} transactions to {OUTPUT_PATH}")