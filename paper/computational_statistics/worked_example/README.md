# Released-wheel quickstart

This example uses the first existing `examples/quickstart.py` vectors in source
order (24 synthetic trials, not participant data). Selection precedes execution.
No recovery, association or real-data fit is authorized by this runner.
Fit uses the release's default configs and deterministic default start; no random
restarts or altered optimizer budget are requested. No simulation RNG is used.

From a fresh directory **outside** the checkout, create a virtual environment:

```powershell
py -3.12 -m venv hgfx-example
./hgfx-example/Scripts/python -m pip install hgfx==1.0.0
./hgfx-example/Scripts/python D:/path/to/hgfx/paper/computational_statistics/worked_example/run.py --output result.json
```

POSIX equivalent:

```sh
python3.12 -m venv hgfx-example
hgfx-example/bin/python -m pip install hgfx==1.0.0
hgfx-example/bin/python /path/to/hgfx/paper/computational_statistics/worked_example/run.py --output result.json
```

Paths to the runner are supplied by the user; no developer data path is required.
The arrays are embedded. The runner enables CPU JAX float64 before imports and
rejects any version other than 1.0.0. Compare module path, environment lock and
hashes with the recorded execution. Output is a smoke/workflow check, not MATLAB
parity or inferential validation.

Local acquisition note: files.pythonhosted.org DNS failed. The wheel was obtained
from the Tsinghua PyPI mirror and its complete bytes matched the SHA-256 in the
official PyPI 1.0.0 JSON metadata:
`5c63c16d93cb2f61d57dacf9b4ba0629215da7c88e61d227cdc0eb60d0d88b90`.
The wheel is not republished here. Dependencies were installed into the external
venv from the local package cache; the lock records their actual versions.
