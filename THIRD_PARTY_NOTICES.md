# Third-Party Notices

HGFX uses third-party projects as frozen compatibility references during development and validation. The Python release is separately packaged and does not require MATLAB or the reference repositories at runtime.

## HGF Toolbox 8.2.0

- Upstream: `https://github.com/ComputationalPsychiatry/hgf-toolbox`
- Frozen compatibility commit: `2437f4dc241541072722a2695ddeca7b44d83dd3`
- Upstream license: MIT
- Upstream copyright: Copyright (c) 2012-2024 Christoph Mathys and contributors
- HGFX location during development/validation: pinned git submodule at `external/hgf-toolbox/`
- Role in HGFX: compatibility oracle and validation reference

The frozen upstream source is not a required HGFX runtime dependency. S10 clean-wheel validation verifies that MATLAB/reference source is not included as runtime payload in the HGFX wheel.

Any source copied or adapted directly from the upstream project must retain the applicable MIT notice and record the upstream path, frozen commit, and adaptation provenance. Behavioral reimplementation against the reference must not be described as copied source unless that provenance is actually present.

## fdlibm numerical algorithms

HGFX contains Python adaptations of selected fdlibm binary64 algorithms solely to make the MATLAB-compatibility numerical path reproducible across host C runtimes.

- Upstream archive: `https://www.netlib.org/fdlibm/`
- Adapted upstream files:
  - `e_exp.c` -> `src/hgfx/math/matlab_exp.py`
  - `s_expm1.c` -> `src/hgfx/math/matlab_exp.py`
  - `e_log.c` -> `src/hgfx/math/matlab_log.py`
- Role in HGFX: portable IEEE-754 `exp`, `expm1`, and `log` arithmetic for frozen D02 numerical compatibility.

The applicable upstream notices are preserved in the adapted source modules. The fdlibm source notices grant permission to use, copy, modify, and distribute the software provided the notices are preserved. `e_exp.c` and `s_expm1.c` carry the 2004 Sun Microsystems notice; `e_log.c` carries the 1993 Sun Microsystems / SunSoft notice.

fdlibm is not an external runtime dependency: the relevant arithmetic has been adapted into the HGFX Python source, with provenance and notices retained.

## PyHGF

- Upstream: `https://github.com/ComputationalPsychiatry/pyhgf`
- v1 release status: **NOT_USED_FOR_V1_RELEASE**

PyHGF was considered during architecture/reuse planning, but the final v1 compatibility specification is the frozen MATLAB HGF Toolbox 8.2.0 above. HGFX v1 does not depend on, vendor, or fork a pinned PyHGF revision for its release implementation. Consequently `reference/PYHGF_VERSION` and `reference/PYHGF_COMMIT` record `NOT_USED_FOR_V1_RELEASE` instead of a fictitious pin.

## Python dependencies

Runtime and optional Python dependencies are declared in `pyproject.toml` and retain their own upstream licenses. This notice does not replace those projects' license texts or metadata.
