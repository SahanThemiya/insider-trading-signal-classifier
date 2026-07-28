from src.data.edgar_client import cik_lookup, fetch_form4_index, fetch_form4_xml

TARGETS = [
    ("COP", "0001209191-23-011018"),
    ("LDOS", "0001628280-23-016441"),
]

cik_map = cik_lookup([t for t, _ in TARGETS])

for ticker, accession in TARGETS:
    cik10 = cik_map[ticker]
    filings = fetch_form4_index(cik10)
    filing = filings[filings["accessionNumber"] == accession].iloc[0]
    xml_bytes = fetch_form4_xml(cik10, filing["accessionNumber"], filing["primaryDocument"])

    print("=" * 80)
    print(ticker, accession, "primaryDocument:", filing["primaryDocument"])
    print(xml_bytes.decode(errors="replace"))