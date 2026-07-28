from src.data.edgar_client import cik_lookup, fetch_form4_index, fetch_form4_xml

CVX_ACCESSION = "0000093410-26-000152"

cik_map = cik_lookup(["XOM", "CVX"])
print("CIKs found:", cik_map)

xom_filings = fetch_form4_index(cik_map["XOM"])
print("XOM form4 filings (all dates):", len(xom_filings))
print(xom_filings.head(10))

cvx_cik = cik_map["CVX"]
filings = fetch_form4_index(cvx_cik)
filing = filings[filings["accessionNumber"] == CVX_ACCESSION].iloc[0]
xml_bytes = fetch_form4_xml(cvx_cik, filing["accessionNumber"], filing["primaryDocument"])

print("primaryDocument:", filing["primaryDocument"])
print(xml_bytes.decode(errors="replace")[:3000])