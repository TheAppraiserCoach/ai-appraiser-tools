import argparse, json, sys
from pathlib import Path
from .build import to_xml, from_xml
from .validate import validate
from .links import check_links


def main(argv=None):
    ap = argparse.ArgumentParser(prog="uad36mismo", description="UAD 3.6 / MISMO 3.6 generator")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("build", help="appraisal JSON -> UAD 3.6 XML (validated)"); s.add_argument("json"); s.add_argument("-o", "--out", required=True)
    s = sub.add_parser("to-json", help="existing UAD 3.6 XML -> editable JSON"); s.add_argument("xml"); s.add_argument("-o", "--out", required=True)
    s = sub.add_parser("validate", help="XSD + relationship-link check on an XML file"); s.add_argument("xml")
    s = sub.add_parser("catalog", help="write the data dictionary (markdown)"); s.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)

    if a.cmd == "build":
        xml = to_xml(json.load(open(a.json)))
        errs = validate(xml) + check_links(xml)
        Path(a.out).write_bytes(xml)
        if errs:
            print(f"WROTE {a.out} but it has {len(errs)} problem(s) UCDP would reject:")
            print("\n".join("  " + e for e in errs[:40])); return 1
        print(f"OK  {a.out}  (schema valid, all relationship links resolve)"); return 0
    if a.cmd == "to-json":
        json.dump(from_xml(open(a.xml, "rb").read()), open(a.out, "w"), indent=1); print("wrote", a.out); return 0
    if a.cmd == "validate":
        xml = open(a.xml, "rb").read(); errs = validate(xml) + check_links(xml)
        print("VALID" if not errs else "\n".join(errs)); return 1 if errs else 0
    if a.cmd == "catalog":
        from .catalog import build_catalog, to_markdown
        rows = build_catalog(); Path(a.out).write_text(to_markdown(rows)); print(len(rows), "entries ->", a.out); return 0


if __name__ == "__main__":
    sys.exit(main())
