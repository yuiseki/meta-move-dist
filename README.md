# meta-move-dist

Dataset: https://huggingface.co/datasets/yuiseki/meta-move-dist

Meta's Movement Distribution from the Humanitarian Data Exchange, kept past
the 90 days HDX holds, and the code that fetches, checks and converts it.
This repository holds the code; the data is on the Hub.

## Where things are

```
scripts/hdx_meta.py           the HDX code shared with study-geoai-algo-py's mirror_hdx_meta.py
scripts/01_download.py        what HDX lists now, nothing deleted; or --from an earlier mirror
scripts/02_verify.py          originals against the manifest; rows, days, Japan, size, no bloom filters
scripts/03_export_parquet.py  every kept CSV -> one table a year, duplicates kept once
src/publish.py                pushes the data and its card to the Hub
tests/                        the HDX code's tests, and adopting

data/README.md                the dataset card. Uploaded as-is
data/LICENSE                  CC BY and what the Parquet changes
data/provenance.yaml          what is kept, the gaps, and what was done
data/manifest.json            every file: HDX name and id, size, sha256, dates, still on HDX or not
data/movement-distribution/   generated: original/ (the CSVs) and the Parquet
```

## Keeping it

```sh
uv run python scripts/01_download.py
uv run python scripts/03_export_parquet.py
uv run python scripts/02_verify.py
uv run python src/publish.py --push
```

HDX adds a file every two weeks or so and drops what is older than about 90
days. Run this at least once a month; a file missed for three months is
gone.

## Three traps

**HDX answers pages with 403.** A plain fetch of a dataset page is refused.
The CKAN API answers with a User-Agent, and every resource URL redirects to a
signed S3 URL that expires; store the API's resource URL, not the S3 one.

**File names lie about their days.** `2026-08-18_to_2026-08-31` holds five
days. 16 days of August 2026 are in no file. Trust `ds`.

**The same day can be in two files.** At the edges of files, and inside four
June files cut by row count. The build keeps one row per region, category
and day, from the file HDX changed last, and checks that the copies agree.

## Licence

The code here is MIT. The data it fetches is CC BY, from AI for Good at Meta:

    Data for Good at Meta, Movement Distribution, Humanitarian Data Exchange
    (https://data.humdata.org/dataset/movement-distribution)
