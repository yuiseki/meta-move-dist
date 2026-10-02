#!/usr/bin/env python3
"""Check the kept originals against their record, and the Parquet against the originals.

Every original must have the size and sha256 in data/manifest.json. The
Parquet must hold the rows the build counted, carry no bloom filters, and
stay below 512 MB a file. The figures below are those of the files kept on
2026-10-02 (2026-06-01 to 2026-08-31); a later fetch adds rows, so they are
lower bounds, and the days already here must keep their rows.
"""

import hashlib
import json
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATASET = "movement-distribution"

AT_LEAST = {"rows": 11735260, "days": 76, "japan_rows": 546312}
FIRST_DAY = "2026-06-01"
JAPAN_REGIONS = 1804


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    failures = []

    def check(ok: bool, what: str) -> None:
        print(("ok    " if ok else "FAIL  ") + what)
        if not ok:
            failures.append(what)

    entry = json.loads((DATA / "manifest.json").read_text())["datasets"][DATASET]
    orig = DATA / DATASET / "original"
    bad = [s["file"] for s in entry["sources"] if sha256(orig / s["file"]) != s["sha256"]]
    check(not bad, f"every original matches the manifest ({len(bad)} do not)")

    files = [DATA / DATASET / n for n in entry["outputs"]]
    lst = ", ".join(f"'{f}'" for f in files)
    con = duckdb.connect()
    rows, days, first, jp, jp_regions = con.sql(
        f"select count(*), count(distinct ds), min(ds)::varchar, "
        f"count(*) filter (where country = 'JPN'), "
        f"count(distinct gadm_id) filter (where country = 'JPN') from read_parquet([{lst}])"
    ).fetchone()
    built = sum(v["rows"] for v in entry["outputs"].values())
    check(rows == built, f"the Parquet holds the {built:,} rows the build counted")
    check(rows >= AT_LEAST["rows"], f"rows {rows:,}, at least {AT_LEAST['rows']:,}")
    check(days >= AT_LEAST["days"], f"days {days}, at least {AT_LEAST['days']}")
    check(first == FIRST_DAY, f"the first day is {first}")
    check(jp >= AT_LEAST["japan_rows"], f"Japan rows {jp:,}, at least {AT_LEAST['japan_rows']:,}")
    check(jp_regions == JAPAN_REGIONS, f"Japan regions {jp_regions:,}")
    big = [f.name for f in files if f.stat().st_size >= 512 * 1024 * 1024]
    check(not big, "every Parquet file is below 512 MB")
    bloom = con.sql(
        f"select count(*) filter (where bloom_filter_offset is not null) from parquet_metadata([{lst}])"
    ).fetchone()[0]
    check(bloom == 0, "no Parquet carries bloom filters")

    if failures:
        print(f"\n{len(failures)} checks failed")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
