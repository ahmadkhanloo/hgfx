from __future__ import annotations

import argparse
from pathlib import Path

from hgfx.golden import import_matlab_json_fixture


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a MATLAB JSON export into an HGFX canonical golden fixture."
    )
    parser.add_argument("raw_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    fixture = import_matlab_json_fixture(args.raw_dir, args.output_dir)
    print("Golden fixture import: PASS")
    print(f"fixture={fixture.path}")
    print(f"model={fixture.metadata['model_name']}")


if __name__ == "__main__":
    main()
