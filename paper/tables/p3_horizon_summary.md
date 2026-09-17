# P3 trial-horizon summary (diagnostic)

Official overall class: `INSUFFICIENT_REFERENCE_EVIDENCE` (`gate_pass=false`). Run `35272347167`.
Do not treat diagnostic PASS rows as a paper-1 identifiability result.

| Model | T | MATLAB/HGFX conv | median r | median sRMSE | scientific_pass |
|---|---:|---|---|---|---|
| hgf_binary | 128 | 0.917 / 0.917 | 0.148 | 1.114 | FAIL |
| hgf_binary | 256 | 0.750 / 0.750 | 0.298 | 1.957 | FAIL |
| hgf_binary | 512 | — | — | — | invalid trajectories retained |
| hgf_binary | 1024 | — | — | — | invalid trajectories retained |
| ehgf_binary | 128 | 0.917 / 0.917 | 0.501 | 2.623 | FAIL |
| ehgf_binary | 256 | 0.917 / 0.917 | 0.480 | 1.995 | FAIL |
| ehgf_binary | 512 | 0.833 / 0.833 | 0.860 | 0.920 | PASS (diagnostic) |
| ehgf_binary | 1024 | 1.000 / 1.000 | 0.838 | 0.690 | PASS (diagnostic) |
| uhgf_binary | 128 | 0.917 / 0.917 | 0.245 | 3.082 | FAIL |
| uhgf_binary | 256 | 0.667 / 0.667 | 0.507 | 2.829 | FAIL |
| uhgf_binary | 512 | 0.750 / 0.750 | 0.750 | 1.169 | FAIL |
| uhgf_binary | 1024 | 0.833 / 0.833 | 0.819 | 0.755 | PASS (diagnostic) |
