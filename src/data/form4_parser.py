from lxml import etree

_PARSER = etree.XMLParser(recover=True)


def _val(parent, tag: str) -> str | None:
    node = parent.find(tag)
    if node is None:
        return None
    value = node.find("value")
    text = value.text if value is not None else node.text
    return value.text if value is not None else node.text


def parse_form4_xml(xml_bytes: bytes, accession_number: str) -> list[dict]:
    root = etree.fromstring(xml_bytes, parser=_PARSER)

    issuer = root.find("issuer")
    ticker = _val(issuer, "issuerTradingSymbol")

    reporting_owner = root.find("reportingOwner")
    owner_name = _val(reporting_owner.find("reportingOwnerId"), "rptOwnerName")
    relationship = reporting_owner.find("reportingOwnerRelationship")
    title = _val(relationship, "officerTitle") or ""
    is_officer = _val(relationship, "isOfficer") == "1"
    is_director = _val(relationship, "isDirector") == "1"

    doc_level_10b5_1 = _val(root, "aff10b5One") == "1"

    footnotes = {fn.get("id"): "".join(fn.itertext()) for fn in root.findall(".//footnotes/footnote")}
    all_footnote_text = " ".join(footnotes.values()).lower()

    rows = []
    for i, txn in enumerate(root.findall(".//nonDerivativeTable/nonDerivativeTransaction")):
        coding = txn.find("transactionCoding")
        amounts = txn.find("transactionAmounts")
        post = txn.find("postTransactionAmounts")
        ownership_nature = txn.find("ownershipNature")
        direct_or_indirect = _val(ownership_nature,
                                  "directOrIndirectOwnership") if ownership_nature is not None else None

        footnote_ids = [fn.get("id") for fn in txn.findall("footnoteId")]
        txn_footnote_text = " ".join(footnotes.get(fid, "") for fid in footnote_ids).lower()
        is_10b5_1 = doc_level_10b5_1 or "10b5-1" in all_footnote_text or "10b5-1" in txn_footnote_text

        rows.append({
            "accession_number": accession_number,
            "row_index": i,
            "ticker": ticker,
            "owner_name": owner_name,
            "title": title,
            "is_officer": is_officer,
            "is_director": is_director,
            "transaction_date": _val(txn, "transactionDate"),
            "transaction_code": _val(coding, "transactionCode"),
            "shares": float(_val(amounts, "transactionShares") or 0),
            "price": float(_val(amounts, "transactionPricePerShare") or 0),
            "acquired_disposed": _val(amounts, "transactionAcquiredDisposedCode"),
            "shares_owned_after": float(_val(post, "sharesOwnedFollowingTransaction") or 0),
            "direct_or_indirect": direct_or_indirect,
            "is_10b5_1": is_10b5_1,
        })
    return rows