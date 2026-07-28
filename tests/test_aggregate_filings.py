import pandas as pd

from src.labeling.aggregate_filings import aggregate_by_filing


def test_aggregate_collapses_multi_tranche_filing():
    df = pd.DataFrame([
        {"accession_number": "A1", "row_index": 0, "ticker": "LMT", "owner_name": "Doe", "title": "CFO",
         "is_officer": True, "is_director": False, "transaction_date": "2026-03-11", "transaction_code": "S",
         "shares": 100, "price": 10.0, "acquired_disposed": "D", "shares_owned_after": 900,
         "is_10b5_1": False, "car": -0.20, "label": 2},
        {"accession_number": "A1", "row_index": 1, "ticker": "LMT", "owner_name": "Doe", "title": "CFO",
         "is_officer": True, "is_director": False, "transaction_date": "2026-03-11", "transaction_code": "S",
         "shares": 200, "price": 20.0, "acquired_disposed": "D", "shares_owned_after": 700,
         "is_10b5_1": False, "car": -0.20, "label": 2},
        {"accession_number": "A2", "row_index": 0, "ticker": "XOM", "owner_name": "Roe", "title": "VP",
         "is_officer": True, "is_director": False, "transaction_date": "2026-01-05", "transaction_code": "P",
         "shares": 50, "price": 15.0, "acquired_disposed": "A", "shares_owned_after": 1050,
         "is_10b5_1": False, "car": 0.05, "label": 1},
    ])

    result = aggregate_by_filing(df)

    assert len(result) == 2

    a1 = result[result["accession_number"] == "A1"].iloc[0]
    assert a1["shares"] == 300
    assert a1["price"] == (100 * 10.0 + 200 * 20.0) / 300
    assert a1["shares_owned_after"] == 700
    assert a1["label"] == 2

    a2 = result[result["accession_number"] == "A2"].iloc[0]
    assert a2["shares"] == 50
    assert a2["price"] == 15.0