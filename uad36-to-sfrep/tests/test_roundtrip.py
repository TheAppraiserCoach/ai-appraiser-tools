"""Every GSE sample must survive XML -> tree -> XML unchanged, and validate against the XSD."""
import sys, glob
from pathlib import Path
from lxml import etree
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from uad36mismo import from_xml, to_xml, validate


def canon(b):
    p = etree.XMLParser(remove_comments=True, remove_blank_text=True)
    r = etree.fromstring(b, p)
    for e in r.iter():
        if isinstance(e.tag, str):
            e.text = (e.text or "").strip() or None
            e.tail = None
    r.attrib.pop("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", None)
    etree.cleanup_namespaces(r)
    return etree.tostring(r, method="c14n")


def main():
    bad = 0
    for f in sorted(glob.glob(str(Path(__file__).resolve().parent.parent / "samples" / "*.xml"))):
        orig = open(f, "rb").read()
        out = to_xml(from_xml(orig))
        errs = validate(out)
        same = canon(orig) == canon(out)
        print(f"{'PASS' if same and not errs else 'FAIL'}  {Path(f).name}  identical={same} schema_errors={len(errs)}")
        if errs:
            print("   ", errs[:3])
        bad += (not same) or bool(errs)
    sys.exit(1 if bad else 0)


main()
