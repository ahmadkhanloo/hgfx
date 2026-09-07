from __future__ import annotations

import argparse
import json
from pathlib import Path

from hgfx.golden import compare_mappings, load_fixture, load_npz_mapping


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare candidate NPZ outputs against an HGFX golden fixture."
    )
    parser.add_argument("fixture_dir", type=Path)
    parser.add_argument("actual_npz", type=Path)
    parser.add_argument("--rtol", type=float, default=1e-11)
    parser.add_argument("--atol", type=float, default=1e-12)
    args = parser.parse_args()

    fixture = load_fixture(args.fixture_dir)
    actual = load_npz_mapping(args.actual_npz)
    report = compare_mappings(
        fixture.expected,
        actual,
        rtol=args.rtol,
        atol=args.atol,
    )
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    raise SystemExit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
