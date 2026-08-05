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

ACCESSION = "0001127602-25-004498"


def test_discretionary_trade_no_10b5_1():
    xml = _BASE.format(aff10b5one="0", footnote_ref="", footnotes="<footnotes/>").encode()
    rows = parse_form4_xml(xml, ACCESSION)

    assert len(rows) == 1
    row = rows[0]
    assert row["accession_number"] == ACCESSION
    assert row["row_index"] == 0
    assert row["ticker"] == "XOM"
    assert row["title"] == "Chief Financial Officer"
    assert row["transaction_code"] == "P"
    assert row["shares"] == 5000
    assert row["price"] == 110.25
    assert row["shares_owned_after"] == 25000
    assert row["is_10b5_1"] is False


def test_doc_level_10b5_1_flag():
    xml = _BASE.format(aff10b5one="1", footnote_ref="", footnotes="<footnotes/>").encode()
    rows = parse_form4_xml(xml, ACCESSION)

    assert rows[0]["is_10b5_1"] is True


def test_footnote_fallback_10b5_1():
    footnotes = '<footnotes><footnote id="F1">Sold pursuant to a Rule 10b5-1 trading plan.</footnote></footnotes>'
    xml = _BASE.format(aff10b5one="0", footnote_ref='<footnoteId id="F1"/>', footnotes=footnotes).encode()
    rows = parse_form4_xml(xml, ACCESSION)

    assert rows[0]["is_10b5_1"] is True


def test_malformed_embedded_tag_recovers():
    footnotes = '<footnotes><footnote id="F1">Note<BR/>pursuant to a Rule 10b5-1 plan</footnote></footnotes>'
    xml = _BASE.format(aff10b5one="0", footnote_ref='<footnoteId id="F1"/>', footnotes=footnotes).encode()
    rows = parse_form4_xml(xml, ACCESSION)

    assert rows[0]["is_10b5_1"] is True


def test_direct_and_indirect_ownership_lines_stay_separate():
    xml = """<?xml version="1.0"?>
    <ownershipDocument>
      <issuer><issuerTradingSymbol>COP</issuerTradingSymbol></issuer>
      <reportingOwner>
        <reportingOwnerId><rptOwnerName>WALKER R A</rptOwnerName></reportingOwnerId>
        <reportingOwnerRelationship><isDirector>1</isDirector><isOfficer>0</isOfficer></reportingOwnerRelationship>
      </reportingOwner>
      <nonDerivativeTable>
        <nonDerivativeTransaction>
          <transactionDate><value>2023-02-17</value></transactionDate>
          <transactionCoding><transactionCode>P</transactionCode></transactionCoding>
          <transactionAmounts>
            <transactionShares><value>4800</value></transactionShares>
            <transactionPricePerShare><value>104.50</value></transactionPricePerShare>
            <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
          </transactionAmounts>
          <postTransactionAmounts><sharesOwnedFollowingTransaction><value>22800</value></sharesOwnedFollowingTransaction></postTransactionAmounts>
          <ownershipNature><directOrIndirectOwnership><value>D</value></directOrIndirectOwnership></ownershipNature>
        </nonDerivativeTransaction>
        <nonDerivativeTransaction>
          <transactionDate><value>2023-02-17</value></transactionDate>
          <transactionCoding><transactionCode>P</transactionCode></transactionCoding>
          <transactionAmounts>
            <transactionShares><value>1200</value></transactionShares>
            <transactionPricePerShare><value>104.50</value></transactionPricePerShare>
            <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
          </transactionAmounts>
          <postTransactionAmounts><sharesOwnedFollowingTransaction><value>5700</value></sharesOwnedFollowingTransaction></postTransactionAmounts>
          <ownershipNature><directOrIndirectOwnership><value>I</value></directOrIndirectOwnership></ownershipNature>
        </nonDerivativeTransaction>
      </nonDerivativeTable>
    </ownershipDocument>""".encode()

    rows = parse_form4_xml(xml, "0001209191-23-011018")

    assert len(rows) == 2
    assert rows[0]["direct_or_indirect"] == "D"
    assert rows[0]["shares"] == 4800
    assert rows[0]["shares_owned_after"] == 22800
    assert rows[1]["direct_or_indirect"] == "I"
    assert rows[1]["shares"] == 1200
    assert rows[1]["shares_owned_after"] == 5700