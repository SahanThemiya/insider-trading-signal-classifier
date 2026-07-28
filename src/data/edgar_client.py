import time

import pandas as pd
import requests

from config import SEC_USER_AGENT

_HEADERS = {"User-Agent": SEC_USER_AGENT}
_REQUEST_DELAY = 0.15


def _get(url: str) -> requests.Response:
    response = requests.get(url, headers=_HEADERS)
    response.raise_for_status()
    time.sleep(_REQUEST_DELAY)
    return response


def cik_lookup(tickers: list[str]) -> dict[str, str]:
    data = _get("https://www.sec.gov/files/company_tickers.json").json()
    lookup = {row["ticker"]: str(row["cik_str"]).zfill(10) for row in data.values()}
    return {ticker: lookup[ticker] for ticker in tickers if ticker in lookup}


def fetch_form4_index(cik10: str) -> pd.DataFrame:
    data = _get(f"https://data.sec.gov/submissions/CIK{cik10}.json").json()
    recent = pd.DataFrame(data["filings"]["recent"])
    return recent.loc[recent["form"] == "4", ["accessionNumber", "filingDate", "primaryDocument"]]


def fetch_form4_xml(cik10: str, accession_number: str, primary_document: str) -> bytes:
    accession_no_dashes = accession_number.replace("-", "")
    cik_no_zeros = str(int(cik10))
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{accession_no_dashes}/{primary_document}"
    return _get(url).content