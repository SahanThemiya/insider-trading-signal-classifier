import pandas as pd

from src.labeling.aggregate_filings import aggregate_by_filing


def test_aggregate_collapses_multi_tranche_filing():
    df = pd.DataFrame([
        {"accession_number": "A1", "row_index": 0, "ticker": "LMT", "owner_name": "Doe", "title": "CFO",
         "is_officer": True, "is_director": False, "transaction_date": "2026-03-11", "transaction_code": "S",
         "shares": 100, "price": 10.0, "acquired_disposed": "D", "shares_owned_after": 900,
         "direct_or_indirect": "D", "is_10b5_1": False, "car": -0.20, "label": 2},
        {"accession_number": "A1", "row_index": 1, "ticker": "LMT", "owner_name": "Doe", "title": "CFO",
         "is_officer": True, "is_director": False, "transaction_date": "2026-03-11", "transaction_code": "S",
         "shares": 200, "price": 20.0, "acquired_disposed": "D", "shares_owned_after": 700,
         "direct_or_indirect": "D", "is_10b5_1": False, "car": -0.20, "label": 2},
        {"accession_number": "A2", "row_index": 0, "ticker": "XOM", "owner_name": "Roe", "title": "VP",
         "is_officer": True, "is_director": False, "transaction_date": "2026-01-05", "transaction_code": "P",
         "shares": 50, "price": 15.0, "acquired_disposed": "A", "shares_owned_after": 1050,
         "direct_or_indirect": "D", "is_10b5_1": False, "car": 0.05, "label": 1},
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


def test_direct_and_indirect_ownership_never_merge():
    df = pd.DataFrame([
        {"accession_number": "B1", "row_index": 0, "ticker": "COP", "owner_name": "Walker", "title": None,
         "is_officer": False, "is_director": True, "transaction_date": "2023-02-17", "transaction_code": "P",
         "shares": 4800, "price": 104.50, "acquired_disposed": "A", "shares_owned_after": 22800,
         "direct_or_indirect": "D", "is_10b5_1": False, "car": 0.02, "label": 1},
        {"accession_number": "B1", "row_index": 1, "ticker": "COP", "owner_name": "Walker", "title": None,
         "is_officer": False, "is_director": True, "transaction_date": "2023-02-17", "transaction_code": "P",
         "shares": 1200, "price": 104.50, "acquired_disposed": "A", "shares_owned_after": 5700,
         "direct_or_indirect": "I", "is_10b5_1": False, "car": 0.02, "label": 1},
    ])

    result = aggregate_by_filing(df)

    assert len(result) == 2
    direct = result[result["direct_or_indirect"] == "D"].iloc[0]
    indirect = result[result["direct_or_indirect"] == "I"].iloc[0]
    assert direct["shares"] == 4800
    assert direct["shares_owned_after"] == 22800
    assert indirect["shares"] == 1200
    assert indirect["shares_owned_after"] == 5700