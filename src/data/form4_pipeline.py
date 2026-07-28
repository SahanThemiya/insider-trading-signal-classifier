import pandas as pd

from src.data.edgar_client import fetch_form4_index, fetch_form4_xml
from src.data.form4_parser import parse_form4_xml


def get_form4_transactions(cik10: str) -> pd.DataFrame:
    rows = []
    for _, filing in fetch_form4_index(cik10).iterrows():
        xml_bytes = fetch_form4_xml(cik10, filing["accessionNumber"], filing["primaryDocument"])
        rows.extend(parse_form4_xml(xml_bytes, filing["accessionNumber"]))
    return pd.DataFrame(rows)