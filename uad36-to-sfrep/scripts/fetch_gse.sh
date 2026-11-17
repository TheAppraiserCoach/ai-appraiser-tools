#!/usr/bin/env bash
# Downloads the official Freddie Mac / Fannie Mae UAD 3.6 schema and sample XML files.
# They are not redistributed in this repo; get them from the source.
set -euo pipefail
cd "$(dirname "$0")/.."
B=https://sf.freddiemac.com/docs/zip
tmp=$(mktemp -d)
curl -fsSL -A "Mozilla/5.0" -o "$tmp/schema.zip" $B/uad-3.6-schema.zip
mkdir -p schema && unzip -qo "$tmp/schema.zip" -d schema
mkdir -p samples
for z in appendix-d-1-urar-sample-scenarios-and-xml-files appendix-d-3-completion-report-sample-scenarios-and-xml-files; do
  curl -fsSL -A "Mozilla/5.0" -o "$tmp/$z.zip" $B/requirements/$z.zip
  mkdir -p "$tmp/$z" && unzip -qo "$tmp/$z.zip" -d "$tmp/$z"
  for inner in "$tmp/$z"/*.zip; do unzip -qjo "$inner" '*.xml' -d samples; done
done
rm -rf "$tmp"
echo "schema/ and samples/ ready"
