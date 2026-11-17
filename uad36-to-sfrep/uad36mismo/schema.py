"""Reads the GSE UAD 3.6 XSD so element ORDER comes from the schema, not from the caller."""
from pathlib import Path
from lxml import etree

XS = "{http://www.w3.org/2001/XMLSchema}"
ROOT = Path(__file__).resolve().parent.parent / "schema" / "GSE_UAD_3.6.0_v1.3"
NS = "http://www.mismo.org/residential/2009/schemas"


class Schema:
    def __init__(self, root: Path = ROOT):
        self.root = Path(root)
        self.xsd_path = self.root / "Combined" / "GSE_UAD_3.6.0_v1.3.xsd"
        self.types = {}      # complexType name -> [(child, type, maxOccurs)]
        self.top = {}        # top-level element name -> type
        self.enums = {}      # simpleType name -> [values]
        for f in sorted((self.root / "Individual").glob("*.xsd")):
            t = etree.parse(str(f)).getroot()
            for ct in t.findall(f"{XS}complexType"):
                seq = ct.find(f"{XS}sequence")
                kids = []
                if seq is not None:
                    for e in seq.iter(f"{XS}element"):
                        kids.append((e.get("name"), e.get("type"), e.get("maxOccurs", "1")))
                self.types[ct.get("name")] = kids
            for e in t.findall(f"{XS}element"):
                self.top[e.get("name")] = e.get("type")
            for st in t.findall(f"{XS}simpleType"):
                vals = [v.get("value") for v in st.iter(f"{XS}enumeration")]
                if vals:
                    self.enums[st.get("name")] = vals

    def child_type(self, parent_type, child):
        for n, t, _ in self.types.get(parent_type, []):
            if n == child:
                return t
        return None

    def order(self, parent_type):
        return [n for n, _, _ in self.types.get(parent_type, [])]
