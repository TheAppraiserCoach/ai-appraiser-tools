# UAD 3.6 to SFREP (Appraise-It Pro) with Claude

Take an appraisal built in Claude and turn it into a UAD 3.6 (MISMO 3.6) XML file that
Appraise-It Pro imports, and that Fannie Mae / Freddie Mac UCDP accepts.

## The idea

1. Claude fills in a JSON tree that mirrors the MISMO 3.6 containers.
2. `uad36mismo build` writes the XML. Element order comes from the official GSE schema, so
   nobody (human or AI) has to remember it.
3. The tool refuses to call the file done until it passes two checks:
   - **Schema check** against the official GSE UAD 3.6 XSD.
   - **Link check** that every `RELATIONSHIP` points at a label that exists. This catches the
     UCDP fatal "The 'from' label included in a RELATIONSHIP container is missing", which
     happens when a source or date field is blank and the dropped container leaves its link behind.
4. In Appraise-It Pro: File, Import, MISMO. Review, add photos, sign, deliver.

## Status

Early release. The generator, schema check, link check and round-trip tests work.
**The generated output has not yet been imported into Appraise-It Pro or submitted to UCDP.**
Test it on a throwaway file before you rely on it, and please open an issue with what you find.
This is a tool, not a substitute for the appraiser's review. You sign the report.

## Setup

    ./scripts/fetch_gse.sh        # downloads the official schema + 14 sample XMLs
    pip install -r requirements.txt
    python3 tests/test_roundtrip.py   # all 14 official samples must round-trip identically

## Use

    python3 -m uad36mismo to-json samples/SF1_Appraisal_v1.4.xml -o report.json   # start from a sample
    # edit report.json (Claude does this), then:
    python3 -m uad36mismo build report.json -o report.xml
    python3 -m uad36mismo validate report.xml
    python3 -m uad36mismo catalog -o DATA-DICTIONARY.md   # every element, definition, allowed values

Tree rules: `"Name": "text"` is a leaf, `{...}` a container, `[...]` a repeat, `"@attr"` an attribute.
Key order does not matter. An element in the wrong place is an error that names the allowed ones.

## What is proven, and what is not

Proven: all 14 official GSE sample files (single family, condo, co-op, manufactured, 2-4 unit,
completion reports) go XML to JSON to XML with no data change and validate against the XSD.

Not yet proven: that Appraise-It Pro imports a file generated from scratch (the samples import
by SFREP's own documentation, but we have not run this tool's output through it), and photo
association. SFREP documents optional MISMO 3.6 image extensions for that (api.sfrep.com/rpti/mismo_36_images.html).
Images travel by MISMO 3.6 plus those extensions, or by RPTI.

## Other SFREP routes

- **RPTI** (zip with AIXML 1.5): covers every Appraise-It form and field, plus PDF and rich text addenda.
- **COM API**: reads and writes fields in an open 3.6 report. Docs at api.sfrep.com.

Schema and sample files belong to Fannie Mae and Freddie Mac and are fetched, not included.

## Working with Claude

Give Claude `report.json` (from `to-json`) and `DATA-DICTIONARY.md` (from `catalog`), plus your
assignment data. Ask it to replace the sample values with the real ones, keep every `xlink:label`
paired with its `RELATIONSHIP`, then run `build`. If `build` reports problems, paste them back to
Claude and repeat. Do not hand-edit around a failed check.

## License

MIT for the code in this repo. The GSE schema and sample files are not included.
