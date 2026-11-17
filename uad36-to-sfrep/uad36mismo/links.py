"""Catches the UCDP fatal "'from' label in a RELATIONSHIP container is missing".

Every RELATIONSHIP's xlink:from / xlink:to must name an xlink:label that exists in the file.
Happens when a source/date field is blank and the vendor drops the container but keeps the link.
"""
from lxml import etree

XLINK = "http://www.w3.org/1999/xlink"


def check_links(xml: bytes):
    root = etree.fromstring(xml)
    labels = {e.get(f"{{{XLINK}}}label") for e in root.iter() if e.get(f"{{{XLINK}}}label")}
    problems = []
    for r in root.iter("{*}RELATIONSHIP"):
        arc = r.get(f"{{{XLINK}}}arcrole", "")
        for end in ("from", "to"):
            v = r.get(f"{{{XLINK}}}{end}")
            if v not in labels:
                problems.append(f"line {r.sourceline}: {arc}: xlink:{end}=\"{v}\" has no matching xlink:label")
    return problems
