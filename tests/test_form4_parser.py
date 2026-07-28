from src.data.form4_parser import parse_form4_xml

_BASE = """<?xml version="1.0"?>
<ownershipDocument>
  <issuer>
    <issuerCik>0000034088</issuerCik>
    <issuerName>EXXON MOBIL CORP</issuerName>
    <issuerTradingSymbol>XOM</issuerTradingSymbol>
  </issuer>
  <reportingOwner>
    <reportingOwnerId>
      <rptOwnerCik>0001234567</rptOwnerCik>
      <rptOwnerName>DOE JANE</rptOwnerName>
    </reportingOwnerId>
    <reportingOwnerRelationship>
      <isDirector>0</isDirector>
      <isOfficer>1</isOfficer>
      <isTenPercentOwner>0</isTenPercentOwner>
      <officerTitle>Chief Financial Officer</officerTitle>
    </reportingOwnerRelationship>
  </reportingOwner>
  <aff10b5One>{aff10b5one}</aff10b5One>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <transactionDate><value>2025-06-02</value></transactionDate>
      <transactionCoding>
        <transactionFormType>4</transactionFormType>
        <transactionCode>P</transactionCode>
      </transactionCoding>
      <transactionAmounts>
        <transactionShares><value>5000</value></transactionShares>
        <transactionPricePerShare><value>110.25</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
      </transactionAmounts>
      <postTransactionAmounts>
        <sharesOwnedFollowingTransaction><value>25000</value></sharesOwnedFollowingTransaction>
      </postTransactionAmounts>
      {footnote_ref}
    </nonDerivativeTransaction>
  </nonDerivativeTable>
  {footnotes}
</ownershipDocument>"""


def test_discretionary_trade_no_10b5_1():
    xml = _BASE.format(aff10b5one="0", footnote_ref="", footnotes="<footnotes/>").encode()
    rows = parse_form4_xml(xml)

    assert len(rows) == 1
    row = rows[0]
    assert row["ticker"] == "XOM"
    assert row["title"] == "Chief Financial Officer"
    assert row["transaction_code"] == "P"
    assert row["shares"] == 5000
    assert row["price"] == 110.25
    assert row["shares_owned_after"] == 25000
    assert row["is_10b5_1"] is False


def test_doc_level_10b5_1_flag():
    xml = _BASE.format(aff10b5one="1", footnote_ref="", footnotes="<footnotes/>").encode()
    rows = parse_form4_xml(xml)

    assert rows[0]["is_10b5_1"] is True


def test_footnote_fallback_10b5_1():
    footnotes = '<footnotes><footnote id="F1">Sold pursuant to a Rule 10b5-1 trading plan.</footnote></footnotes>'
    xml = _BASE.format(aff10b5one="0", footnote_ref='<footnoteId id="F1"/>', footnotes=footnotes).encode()
    rows = parse_form4_xml(xml)

    assert rows[0]["is_10b5_1"] is True