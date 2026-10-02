---
license: cc-by-4.0
language:
- en
task_categories:
- time-series-forecasting
- tabular-regression
tags:
- human-mobility
- meta
- data-for-good
- hdx
- gadm
size_categories:
- 10M<n<100M
configs:
- config_name: default
  data_files: movement-distribution/*.parquet
---

# meta-move-dist

Meta's Movement Distribution, kept beyond the 90 days HDX holds: for every
administrative region of 217 countries and every day, how far from home the
people of that region went, as the share at no distance, under 10 km, 10 to
100 km, and over 100 km. 2026-06-01 onward, from Facebook users who share
their location.

CC BY 4.0. Credit Data for Good at Meta and the Humanitarian Data Exchange
(see Licence).

## Why this exists

AI for Good at Meta (formerly Data for Good at Meta) publishes Movement
Distribution on the Humanitarian Data Exchange in files of four days to two
weeks, and HDX keeps only about the last 90 days: older files are removed.
A time series longer than three months exists only where someone kept the
files. This dataset keeps every file it has fetched, unchanged, and rebuilds
one table from all of them.

## What is here

| | rows | days |
|---|---:|---|
| `movement-distribution/movement_distribution_2026.parquet` | 11,735,260 | 2026-06-01 to 2026-08-31, 76 of 92 |

| column | |
|---|---|
| `gadm_id`, `gadm_name` | the region, its GADM id and name (`JPN.41.51_1`, `Taitō`) |
| `country` | ISO 3166-1 alpha-3 |
| `polygon_level` | GADM level, an integer |
| `home_to_ping_distance_category` | `0`, `(0, 10)`, `[10, 100)`, `100+`, km from home |
| `distance_category_ping_fraction` | the share of the region's people in that category that day |
| `ds` | the day, a date |
| `source_file` | added here: the original file the row was taken from |

38,943 regions. Japan is 1,804 municipalities (GADM level 2), all 53 of
Tokyo among them; 546,312 rows.

`movement-distribution/original/` holds every file HDX has served, byte for
byte: 12 CSVs and the readme PDF so far. `manifest.json` lists each with its
HDX name and resource id, sizes, sha256, HDX's own dates, when it was
fetched, and whether HDX still lists it.

## Things to know

**Days are missing.** 16 days of August 2026 are in no file: 4, 5, 7, 9, 10,
13, 17, 19 to 22, 24, 26 and 28 to 30. The file named `2026-08-18_to_2026-08-31`
holds 18, 23, 25, 27 and 31 only. Trust `ds`, not the file names.

**Files overlap.** The same days appear in two files at their edges (06-15
and 06-16, 07-01, 08-01; 617,668 rows), always with the same values. Each row
is kept once, from the file HDX changed last. Four June files are cut by row
count, not by day, so 06-19, 06-23 and 06-27 are split between two files.

**The shares are noisy on purpose.** Meta adds noise and drops small
regions. 301,846 rows have a negative share, and the four shares of a region
and day need not add up to 1.

**Regions changed in March 2026.** Meta re-drew some regions then; some that
existed before do not now.

```sql
-- DuckDB, straight off the Hub: how far the people of Taito ward went
SELECT ds, home_to_ping_distance_category, round(distance_category_ping_fraction, 3)
FROM 'hf://datasets/yuiseki/meta-move-dist/movement-distribution/movement_distribution_2026.parquet'
WHERE country = 'JPN' AND gadm_id = 'JPN.41.51_1' AND ds = DATE '2026-07-14'
ORDER BY 2;
```

## Keeping it

```bash
git clone https://github.com/yuiseki/meta-move-dist
cd meta-move-dist
uv run python scripts/01_download.py      # what HDX lists now; nothing is deleted
uv run python scripts/03_export_parquet.py
uv run python scripts/02_verify.py
uv run python src/publish.py --push
```

HDX adds a file every two weeks or so. A run that misses one for three
months loses it for good.

## Licence

CC BY 4.0, as HDX lists the dataset (`cc-by`). Credit as HDX asks:

    Data for Good at Meta, Movement Distribution, Humanitarian Data Exchange
    (https://data.humdata.org/dataset/movement-distribution)

The originals are Meta's, unchanged. The Parquet is made from them; `LICENSE`
beside this file says what was done.
