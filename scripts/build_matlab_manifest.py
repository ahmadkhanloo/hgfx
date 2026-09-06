from __future__ import annotations

from pathlib import Path
import hashlib
import sys


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/build_matlab_manifest.py <hgf-toolbox-root>")

    root = Path(sys.argv[1]).resolve()
    files = sorted(root.rglob("*.m"))

    for path in files:
        rel = path.relative_to(root)
        print(f"{rel.as_posix()}\t{sha256(path)}")


if __name__ == "__main__":
    main()
