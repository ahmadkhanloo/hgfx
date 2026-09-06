from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "external/hgf-toolbox").resolve()
for p in sorted((x for x in root.rglob("*.m") if x.is_file()), key=lambda x: x.relative_to(root).as_posix()):
    print(f"{p.relative_to(root).as_posix()}\t{sha256(p.read_bytes()).hexdigest()}")
