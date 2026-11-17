"""JSON tree <-> MISMO 3.6 XML.

Tree conventions
  "NAME": "text" | 12 | true     leaf element
  "NAME": {...}                   container; "@attr" keys are attributes, "#text" is leaf text
  "NAME": [ ... ]                 repeated element
Key order is irrelevant: children are emitted in the order the XSD requires.
"""
from lxml import etree
from .schema import Schema, NS

XLINK = "http://www.w3.org/1999/xlink"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
GSE = "http://www.datamodelextension.org"
NSMAP = {None: NS, "xlink": XLINK, "gse": GSE, "xsi": XSI}
MODEL_ID = "3.6.0366"
_schema = None


def schema():
    global _schema
    if _schema is None:
        _schema = Schema()
    return _schema


def _q(name):
    if ":" in name:
        p, n = name.split(":", 1)
        return "{%s}%s" % ({"xlink": XLINK, "xsi": XSI, "gse": GSE}[p], n)
    return name


def _txt(v):
    if v is True:
        return "true"
    if v is False:
        return "false"
    return str(v)


def _emit(parent, name, val, ptype, sc, path):
    ctype = sc.child_type(ptype, name) if ptype else None
    if ptype and ctype is None:
        raise ValueError(f"{path}: <{name}> is not allowed inside {ptype}; allowed: {sc.order(ptype)}")
    ns_name = "{%s}%s" % (NS, name)
    items = val if isinstance(val, list) else [val]
    for it in items:
        el = etree.SubElement(parent, ns_name)
        if isinstance(it, dict):
            for k, v in it.items():
                if k.startswith("@"):
                    el.set(_q(k[1:]), _txt(v))
            if "#text" in it:
                el.text = _txt(it["#text"])
            kids = {k: v for k, v in it.items() if not k.startswith("@") and k != "#text"}
            _children(el, kids, ctype, sc, f"{path}/{name}")
        elif it is None:
            el.set("{%s}nil" % XSI, "true")
        else:
            el.text = _txt(it)


def _children(el, kids, ctype, sc, path):
    if not kids:
        return
    order = sc.order(ctype) if ctype else list(kids)
    unknown = [k for k in kids if k not in order]
    if unknown:
        raise ValueError(f"{path}: {unknown} not allowed in {ctype}; allowed in order: {order}")
    for name in order:
        if name in kids:
            _emit(el, name, kids[name], ctype, sc, path)


def to_xml(tree: dict, model_id: str = MODEL_ID) -> bytes:
    """tree = {"MESSAGE": {...}} or the MESSAGE body itself."""
    sc = schema()
    body = tree.get("MESSAGE", tree)
    root = etree.Element("{%s}MESSAGE" % NS, nsmap=NSMAP)
    root.set("MISMOReferenceModelIdentifier", body.get("@MISMOReferenceModelIdentifier", model_id))
    kids = {k: v for k, v in body.items() if not k.startswith("@")}
    _children(root, kids, "MESSAGE", sc, "MESSAGE")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)


def _local(el):
    return etree.QName(el).localname


def _pfx(qn):
    q = etree.QName(qn)
    return {XLINK: "xlink:", XSI: "xsi:", GSE: "gse:"}.get(q.namespace, "") + q.localname


def _node(el):
    attrs = {"@" + _pfx(k): v for k, v in el.attrib.items()}
    kids = [c for c in el if isinstance(c.tag, str)]
    if not kids:
        if attrs.get("@xsi:nil") == "true":
            return None
        txt = (el.text or "").strip()
        if attrs:
            return {**attrs, "#text": txt}
        return txt
    d = dict(attrs)
    multi = set()
    for c in kids:
        n = _local(c)
        v = _node(c)
        if n in multi:
            d[n].append(v)
        elif n in d:
            d[n] = [d[n], v]
            multi.add(n)
        else:
            d[n] = v
    return d


def from_xml(data: bytes) -> dict:
    """Parse an existing UAD 3.6 file into the tree form (comments dropped)."""
    root = etree.fromstring(data)
    body = _node(root)
    body.pop("@xsi:schemaLocation", None)
    return {"MESSAGE": body}
