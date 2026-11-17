from lxml import etree
from .schema import Schema

_xsd = None


def validate(xml: bytes):
    """Return a list of schema error strings; empty list = valid against GSE UAD 3.6 v1.3."""
    global _xsd
    if _xsd is None:
        _xsd = etree.XMLSchema(etree.parse(str(Schema().xsd_path)))
    doc = etree.fromstring(xml)
    if _xsd.validate(doc):
        return []
    return [f"line {e.line}: {e.message}" for e in _xsd.error_log]
