"""Column mapping for any MLS export.

Every MLS names its fields differently (Flexmls "Apx Acreage", Teton "Acres", Paragon
"Lot Acres"...). This module guesses which export column feeds each field the model needs,
and the app lets the user correct the guess with dropdowns before running.

A field maps to a LIST of source columns. Numeric fields are summed across them (so Teton's
"Main House Baths-Full" + "Main House Baths-3/4" become full baths, and "Main Level SqFt" +
"2nd Flr & Above SqFt" become above-grade area). Text fields are joined with ", ".
"""
import re

import pandas as pd

# key, label, required, kind (num | text | date | flag), synonyms (regex on normalized header),
# multi (allow several columns summed/joined), extra patterns that pull in sibling columns
FIELDS = [
    ("sold_price", "Sold price", True, "num",
     [r"^sold price$", r"^sale price$", r"^clos(e|ing) price$", r"^sold$", r"^price sold$", r"^sp$",
      r"sold price", r"sale price", r"close price"], False, []),
    ("sold_date", "Sold / closing date", True, "date",
     [r"^sold date$", r"^close date$", r"^closing date$", r"^sale date$", r"^date sold$", r"^sold dt$",
      r"sold date", r"clos(e|ing) date", r"sale date"], False, []),
    ("beds", "Bedrooms", True, "num",
     [r"^bedrooms$", r"^beds$", r"^total bedrooms$", r"^bedrooms total$", r"^br$", r"^# bedrooms$",
      r"^main house total bedrooms$", r"^overall total bedrooms$", r"bedroom"], False, []),
    ("full_baths", "Full bathrooms (3/4 baths count as full)", True, "num",
     [r"^bathrooms$", r"^full baths$", r"^baths full$", r"^full bathrooms$", r"^total full baths$",
      r"^baths-full$", r"^main house baths-full$", r"^bathrooms full$", r"^fb$", r"full bath", r"baths?-full"],
     True, [r"baths?-3/4$", r"^3/4 baths?$", r"three quarter bath", r"baths? 3/4"]),
    ("half_baths", "Half bathrooms", False, "num",
     [r"^total half baths$", r"^half baths$", r"^baths half$", r"^half bathrooms$", r"^baths-half$",
      r"^main house baths-half$", r"^1/2 baths?$", r"^hb$", r"half bath", r"baths?-half"], True, []),
    ("abv_sqft", "Above-grade living area (GLA)", True, "num",
     [r"^abv grade sqft$", r"^above grade sqft$", r"^above grade (finished )?(sq ?ft|area)$", r"^gla$",
      r"^living area$", r"^sqft above grade$", r"^above grade$", r"^ag sqft$", r"^main house-main level sqft$",
      r"^finished sqft above grade$", r"above grade", r"^sq ?ft living", r"living (sq ?ft|area)", r"^gla "],
     True, [r"2nd fl(oo)?r & above sqft", r"^upper sqft$", r"^upper level sqft$", r"^main house-main level sqft$"]),
    ("total_sqft", "Total sqft (used only if GLA is missing)", False, "num",
     [r"^apx total sqft$", r"^total sqft$", r"^total sq ?ft$", r"^overall livable sqft$", r"^main house sqft$",
      r"^sqft$", r"^square feet$", r"^total square feet$", r"^living sqft total$", r"total sq ?ft", r"^sq ?ft total"],
     False, []),
    ("blw_sqft", "Below-grade / basement sqft", False, "num",
     [r"^blw grade sqft$", r"^below grade sqft$", r"^basement sqft$", r"^bsmt sqft$", r"^below grade$",
      r"^main house-bg sqft finished$", r"^lower sqft$", r"^lower level sqft$", r"below grade", r"basement sq ?ft",
      r"bg sqft"], True, [r"bg sqft (finished|unfinished)$", r"^basement sqft (finished|unfinished)$"]),
    ("acreage", "Lot size in acres", True, "num",
     [r"^apx acreage$", r"^acreage$", r"^acres$", r"^lot acres$", r"^lot size \(?acres\)?$", r"^lot size acres$",
      r"^acres apx$", r"^approx acres$", r"acre"], False, []),
    ("year_built", "Year built", True, "num",
     [r"^apx year built$", r"^year built$", r"^yr built$", r"^yearbuilt$", r"^built$", r"^year blt$", r"year built",
      r"yr built"], False, []),
    ("street_no", "Street number", False, "text",
     [r"^street #$", r"^street number$", r"^number$", r"^house number$", r"^st #$", r"^street num$", r"^st number$",
      r"^address number$", r"^str #$", r"street (#|number|num)$"], False, []),
    ("street_name", "Street name", False, "text",
     [r"^street/road name$", r"^street name$", r"^street$", r"^road name$", r"^st name$", r"^str name$",
      r"^address street$", r"street name"], True, [r"^street suffix$", r"^st suffix$", r"^street type$", r"^suffix$",
                                                    r"^street dir(ection)?$", r"^post direction$"]),
    ("full_address", "Full street address (if number and name are not separate)", False, "text",
     [r"^address$", r"^short address$", r"^property address$", r"^street address$", r"^full address$",
      r"^site address$", r"^situs address$", r"^address 1$", r"^prop address$", r"^addr$"], False, []),
    ("city", "City", True, "text",
     [r"^city$", r"^city/town$", r"^town$", r"^municipality$", r"^city name$", r"^postal city$", r"^city$"], False, []),
    ("state", "State", True, "text",
     [r"^state$", r"^state/province$", r"^st$", r"^state or province$", r"^state code$"], False, []),
    ("zip", "ZIP code", False, "text",
     [r"^zip code$", r"^zip$", r"^postal code$", r"^zipcode$", r"^zip/postal code$", r"^postal$", r"zip"], False, []),
    ("garage", "Garage (stalls and/or type)", False, "text",
     [r"^garage # stalls/type$", r"^garage$", r"^garage stalls$", r"^garage spaces$", r"^# garage stalls$",
      r"^garage type$", r"^main house # stalls$", r"^garage capacity$", r"^parking$", r"^garage/parking$",
      r"^# of garage$", r"garage (stalls|spaces|type|cap)", r"^garage"], True, [r"^main house garage type$",
                                                                                   r"^garage type$", r"^garage description$"]),
    ("fireplaces", "Fireplaces (count)", False, "num",
     [r"^fireplace$", r"^fireplaces$", r"^# fireplaces$", r"^fireplace count$", r"^fireplaces total$",
      r"^# of fireplaces$", r"^fireplace #$", r"fireplace"], True, [r"^fireplace: .* #$", r"^fireplaces?: .*#$"]),
    ("patio_deck", "Patio / deck", False, "text",
     [r"^patio/deck$", r"^patio deck$", r"^patio$", r"^deck$", r"^patio & deck$", r"^patio/porch/deck$",
      r"^exterior features$", r"patio", r"deck"], True, [r"^patio and porch", r"^exterior features: (deck|patio|porch)"]),
    ("ac", "Air conditioning", False, "flag",
     [r"^air conditioning$", r"^cooling$", r"^a/c$", r"^ac$", r"^central air$", r"^air cond", r"^cooling type$",
      r"air conditioning", r"cooling"], True, [r"^air conditioning: central air$", r"^cooling: central", r"^ac: central"]),
    ("hoa", "HOA (yes/no or fee)", False, "flag",
     [r"^hoa$", r"^hoa y/n$", r"^hoa yn$", r"^has hoa$", r"^hoa fee$", r"^hoa fee amount$", r"^association fee$",
      r"^ann\.? hoa fee$", r"^annual hoa fee$", r"^hoa dues$", r"^association$", r"^hoa "], False, []),
    ("view", "View", False, "flag",
     [r"^view$", r"^views$", r"^view description$", r"^view type$", r"^views?: ", r"^view "], True, [r"^views?: "]),
    ("subdivision", "Subdivision (map summaries)", False, "text",
     [r"^subdivision$", r"^subdivision name$", r"^neighborhood$", r"^subdiv$", r"^development$", r"^area$",
      r"^community$", r"subdivision"], False, []),
    ("mls_number", "MLS number", False, "text",
     [r"^mls number$", r"^mls #$", r"^mls$", r"^listing number$", r"^mls id$", r"^listing id$", r"^ml #$",
      r"^mlsnumber$", r"^list number$", r"mls ?(#|number|id)"], False, []),
    ("list_price", "List price", False, "num",
     [r"^list price$", r"^listing price$", r"^lp$", r"^current list price$", r"^asking price$", r"list price"], False, []),
    ("orig_list_price", "Original list price", False, "num",
     [r"^original list price$", r"^orig\.? list price$", r"^olp$", r"^original price$", r"orig(inal)?\.? list"], False, []),
    ("dom", "Days on market", False, "num",
     [r"^days on market$", r"^dom$", r"^cdom$", r"^agent days on market$", r"^days to sell$", r"^market days$",
      r"days on market"], False, []),
    ("seller_conc", "Seller concessions", False, "text",
     [r"^seller conc$", r"^seller concessions$", r"^concessions$", r"^seller paid$", r"^seller credit", r"concession"],
     False, []),
]
FIELD_BY_KEY = {f[0]: f for f in FIELDS}
PARTS_ONLY = {"abv_sqft", "blw_sqft"}   # siblings are floor levels, not add-ons
MULTI = {f[0] for f in FIELDS if f[5]}
REQUIRED = [f[0] for f in FIELDS if f[2]]
ADDRESS_NOTE = ("Address: either street number + street name, or one full-address column, "
                "plus city and state, is needed for the map and comp finder.")


def norm(h: str) -> str:
    h = str(h).strip().lstrip("﻿").replace("²", "").lower()
    h = re.sub(r"\s+", " ", h)
    h = re.sub(r"[“”\"']", "", h)
    return h


def _score(header_n: str, patterns: list[str]) -> int:
    """Earlier patterns in the list win; anchored patterns outrank loose ones."""
    for i, p in enumerate(patterns):
        if re.search(p, header_n):
            anchored = p.startswith("^") and p.endswith("$")
            return (200 if anchored else 100) - i
    return 0


def guess(columns: list[str]) -> dict[str, list[str]]:
    """Return {field_key: [source columns]} best guesses. Each source column is used once."""
    cols = list(columns)
    normed = {c: norm(c) for c in cols}
    taken: set[str] = set()
    mapping: dict[str, list[str]] = {}
    # pass 1: anchored/strong matches, in field order
    for key, _label, _req, _kind, pats, multi, extra in FIELDS:
        best, best_s = None, 0
        for c in cols:
            if c in taken:
                continue
            s = _score(normed[c], pats)
            if s > best_s:
                best, best_s = c, s
        chosen = []
        if best is not None and best_s > 0:
            chosen.append(best)
            taken.add(best)
        if multi:
            # For area fields the siblings are LEVELS (main level + upper level). Only add them when
            # the primary pick is itself a level, never on top of an explicit above-grade total,
            # or the floors get counted twice.
            primary_is_part = best is not None and any(re.search(p, normed[best]) for p in extra)
            if key not in PARTS_ONLY or best is None or primary_is_part:
                for c in cols:
                    if c in taken:
                        continue
                    if any(re.search(p, normed[c]) for p in extra):
                        chosen.append(c)
                        taken.add(c)
        mapping[key] = chosen
    # Flexmls-style "Garage # Stalls/Type" already carries the type; Teton splits stalls and type,
    # both land in `garage` through the extra patterns. Nothing else to do here.
    return mapping


# ---------- building the canonical frame ----------
def _to_num(s: pd.Series) -> pd.Series:
    txt = s.fillna("").astype(str).str.replace(r"[,$]", "", regex=True).str.strip()
    out = pd.to_numeric(txt, errors="coerce")
    # "2 Stalls, Attached" / "3, Gas" -> first integer
    need = out.isna() & (txt != "")
    if need.any():
        out[need] = pd.to_numeric(txt[need].str.extract(r"(\d+(?:\.\d+)?)")[0], errors="coerce")
    return out


def _num_sum(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    if not cols:
        return pd.Series(float("nan"), index=df.index)
    parts = [_to_num(df[c]) for c in cols if c in df.columns]
    if not parts:
        return pd.Series(float("nan"), index=df.index)
    stacked = pd.concat(parts, axis=1)
    all_blank = stacked.isna().all(axis=1)
    out = stacked.fillna(0).sum(axis=1)
    out[all_blank] = float("nan")
    return out


def _text_join(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    if not cols:
        return pd.Series("", index=df.index)
    parts = [df[c].fillna("").astype(str).str.strip() for c in cols if c in df.columns]
    if not parts:
        return pd.Series("", index=df.index)
    return pd.concat(parts, axis=1).apply(lambda r: ", ".join(v for v in r if v), axis=1)


NO_WORDS = {"", "no", "none", "n", "0", "false", "n/a", "na", "-"}


def _flag(df: pd.DataFrame, cols: list[str], must_contain: str | None = None) -> pd.Series:
    """1 when any mapped column says yes. A yes is: a number > 0, or any text that is not a
    no-word (and, when must_contain is given, contains that word, e.g. 'central')."""
    if not cols:
        return pd.Series(0, index=df.index)
    out = pd.Series(0, index=df.index)
    for c in cols:
        if c not in df.columns:
            continue
        txt = df[c].fillna("").astype(str).str.strip()
        low = txt.str.lower()
        num = pd.to_numeric(txt.str.replace(r"[,$]", "", regex=True), errors="coerce")
        yes = (num > 0) | (num.isna() & ~low.isin(NO_WORDS))
        if must_contain and norm(c).find(must_contain) < 0:
            # a generic "Air Conditioning" text column: only count it when the text names central
            yes = yes & low.str.contains(must_contain)
        out = out | yes.astype(int)
    return out


def _garage(df: pd.DataFrame, cols: list[str]) -> tuple[pd.Series, pd.Series]:
    txt = _text_join(df, cols)
    spaces = txt.str.extract(r"(\d+)")[0].fillna(0).astype(int)

    def gtype(x):
        xs = str(x)
        if xs.strip() == "":
            return "None"
        for t in ("Attached", "Detached", "Carport"):
            if t.lower() in xs.lower():
                return t
        return "Other" if re.search(r"\d", xs) or len(xs) > 0 else "None"
    return spaces, txt.apply(gtype)


def apply_mapping(raw: pd.DataFrame, mapping: dict[str, list[str]]) -> pd.DataFrame:
    """Return a frame with the canonical columns core.py expects, built from any export."""
    m = {k: [c for c in v if c in raw.columns] for k, v in mapping.items()}
    df = pd.DataFrame(index=raw.index)
    df["sold_price"] = _num_sum(raw, m.get("sold_price", []))
    df["list_price"] = _num_sum(raw, m.get("list_price", []))
    df["orig_list_price"] = _num_sum(raw, m.get("orig_list_price", []))
    df["dom"] = _num_sum(raw, m.get("dom", []))
    df["beds"] = _num_sum(raw, m.get("beds", []))
    df["full_baths"] = _num_sum(raw, m.get("full_baths", []))
    df["half_baths"] = _num_sum(raw, m.get("half_baths", [])).fillna(0)
    df["acreage"] = _num_sum(raw, m.get("acreage", []))
    df["year_built"] = _num_sum(raw, m.get("year_built", []))
    df["abv_sqft"] = _num_sum(raw, m.get("abv_sqft", []))
    df["blw_sqft"] = _num_sum(raw, m.get("blw_sqft", [])).fillna(0)
    df["total_sqft"] = _num_sum(raw, m.get("total_sqft", []))
    # GLA fallback: total minus below grade when no above-grade column exists
    no_abv = df["abv_sqft"].isna() | (df["abv_sqft"] <= 0)
    df.loc[no_abv, "abv_sqft"] = (df.loc[no_abv, "total_sqft"] - df.loc[no_abv, "blw_sqft"])
    df.loc[df["abv_sqft"] <= 0, "abv_sqft"] = float("nan")
    df["bsmt_sqft"] = df["blw_sqft"]
    dates = _text_join(raw, m.get("sold_date", []))
    df["sold_date"] = pd.to_datetime(dates, errors="coerce")
    # address pieces for the Census geocoder (keeps core.geocode_batch's column names)
    if m.get("street_no") or m.get("street_name"):
        df["Street #"] = _text_join(raw, m.get("street_no", []))
        df["Street/Road Name"] = _text_join(raw, m.get("street_name", [])).str.replace(", ", " ")
    else:
        full = _text_join(raw, m.get("full_address", []))
        split = full.str.extract(r"^\s*(\d+[A-Za-z\-]*)\s+(.*)$")
        df["Street #"] = split[0].fillna("")
        df["Street/Road Name"] = split[1].fillna(full)
    df["City"] = _text_join(raw, m.get("city", []))
    df["State"] = _text_join(raw, m.get("state", []))
    df["Zip Code"] = _text_join(raw, m.get("zip", [])).str.extract(r"(\d{5})")[0].fillna("")
    # features, already engineered so core.engineer() can take them as-is
    df["garage_spaces"], df["garage_type"] = _garage(raw, m.get("garage", []))
    df["fireplaces"] = _num_sum(raw, m.get("fireplaces", [])).fillna(0)
    patio = _text_join(raw, m.get("patio_deck", []))
    df["patio_deck_ct"] = patio.apply(lambda x: (lambda n: n if n is not None else (1 if x.strip() and x.strip().lower() not in NO_WORDS else 0))(
        int(re.search(r"\d+", x).group()) if re.search(r"\d+", x) else None))
    df["has_ac"] = _flag(raw, m.get("ac", []), must_contain="central")
    df["hoa"] = _flag(raw, m.get("hoa", []))
    df["has_view"] = _flag(raw, m.get("view", []))
    df["Subdivision"] = _text_join(raw, m.get("subdivision", []))
    df["MLS Number"] = _text_join(raw, m.get("mls_number", []))
    df["Seller Conc"] = _text_join(raw, m.get("seller_conc", []))
    return df


def missing_required(mapping: dict[str, list[str]]) -> list[str]:
    miss = [FIELD_BY_KEY[k][1] for k in REQUIRED if not mapping.get(k)]
    if not (mapping.get("street_no") and mapping.get("street_name")) and not mapping.get("full_address"):
        miss.append("Street address (number + name, or one full-address column)")
    return miss
