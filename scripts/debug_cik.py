import requests

from config import SEC_USER_AGENT

data = requests.get(
    "https://www.sec.gov/files/company_tickers.json",
    headers={"User-Agent": SEC_USER_AGENT},
).json()

matches = [row for row in data.values() if row["ticker"] == "XOM"]
print(matches)