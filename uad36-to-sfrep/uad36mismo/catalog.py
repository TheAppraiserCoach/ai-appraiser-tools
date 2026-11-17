"""Data dictionary for Claude: every element path in the UAD 3.6 schema with its docs and allowed values."""
from lxml import etree
from .schema import Schema, XS


def build_catalog(sc: Schema = None):
    sc = sc or Schema()
    docs, etype = {}, {}
    for f in sorted((sc.root / "Individual").glob("*.xsd")):
        t = etree.parse(str(f)).getroot()
        for ct in t.findall(f"{XS}complexType"):
            seq = ct.find(f"{XS}sequence")
            if seq is None:
                continue
            for e in seq.iter(f"{XS}element"):
                d = e.find(f"{XS}annotation/{XS}documentation")
                docs[(ct.get("name"), e.get("name"))] = (d.text or "").strip() if d is not None else ""
                etype[(ct.get("name"), e.get("name"))] = e
    rows = []

    def walk(tname, path, seen):
        for name, ctype, mx in sc.types.get(tname, []):
            p = path + "/" + name
            e = etype.get((tname, name))
            req = e is not None and e.get("minOccurs", "1") != "0"
            is_enum = bool(ctype) and ctype.endswith("Enum") and (ctype[:-4] + "Base") in sc.enums
            if is_enum:
                rows.append((p, ctype, "|".join(sc.enums[ctype[:-4] + "Base"]), req, mx != "1", docs.get((tname, name), "")))
            elif ctype in sc.types and ctype not in seen and sc.types[ctype]:
                rows.append((p, "container", "", req, mx != "1", docs.get((tname, name), "")))
                walk(ctype, p, seen | {ctype})
            else:
                base = ctype
                rows.append((p, base, "", req, mx != "1", docs.get((tname, name), "")))

    walk(sc.top.get("MESSAGE", "MESSAGE"), "MESSAGE", {"MESSAGE"})
    return rows


def to_markdown(rows):
    out = ["# UAD 3.6 data dictionary (generated from GSE_UAD_3.6.0_v1.3 XSD)", "",
           "path | type | required | repeats | allowed values | definition", "--- | --- | --- | --- | --- | ---"]
    for p, t, enum, req, rep, doc in rows:
        out.append(f"`{p}` | {t} | {'yes' if req else ''} | {'yes' if rep else ''} | {enum} | {doc.replace('|', '/')[:300]}")
    return "\n".join(out) + "\n"
