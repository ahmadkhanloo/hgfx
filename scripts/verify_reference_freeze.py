from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "external" / "hgf-toolbox"
REF = ROOT / "reference"
EXPECTED = "2437f4dc241541072722a2695ddeca7b44d83dd3"


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not SUB.exists():
        fail("initialize the submodule with: git submodule update --init")

    head = run("git", "-C", str(SUB), "rev-parse", "HEAD")
    if head != EXPECTED:
        fail(f"submodule HEAD {head} != expected {EXPECTED}")

    rows = []
    for line in (REF / "matlab_manifest.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        if line.strip():
            path, blob, size = line.split("\t")
            rows.append((path, blob, int(size)))

    actual = sorted(
        p.relative_to(SUB).as_posix()
        for p in SUB.rglob("*.m")
        if p.is_file()
    )
    expected_paths = sorted(path for path, _, _ in rows)
    if actual != expected_paths:
        fail("MATLAB file list differs from frozen manifest")

    bad = []
    for path, expected_blob, expected_size in rows:
        p = SUB / path
        blob = run("git", "-C", str(SUB), "hash-object", str(p))
        if blob != expected_blob or p.stat().st_size != expected_size:
            bad.append(path)

    if bad:
        fail(f"content mismatch for {len(bad)} files: {bad[:10]}")

    print("Reference freeze verification: PASS")
    print(f"commit={head}")
    print(f"matlab_files={len(rows)}")


if __name__ == "__main__":
    main()
