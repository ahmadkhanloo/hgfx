#!/usr/bin/env python3
"""PERF-01D / issue #90: SHA-verified cross-host FLOAT diagnostic audit.

This is not a fitting, statistical, performance, GPU, or independent-review
test. An exact archived binary64 diagnostic value may differ by ulps across
execution environments; mismatch is MEASURED, never silently accepted as a
scientific or bitwise-replay PASS.
"""
from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import struct
import sys

import numpy as np

RUN = "42187240378"
CANDIDATE = "5fdb627244c12d1ebd7582f83cc2c0783fb3cd5d"
SHA = {
    "hgfx_raw.json": "060247be69f8542cf0c7e30d5cf12fb93e12411737452a308e489fef9e220fce",
    "matlab_raw.json": "4816a4bf52c86d383363e6b957376e66e33a825be482de9ff3c75b557590ff2a",
}
STATUS = "ENGINEERING_ULP_MEASUREMENTS_ONLY_NOT_EXACT_REPLAY_PASS"
N = 24


def bits(x: float) -> str:
    return struct.pack(">d", float(x)).hex()


def ulp_distance(a: float, b: float) -> int:
    """Distance in representable binary64 values, for finite scalar pairs."""
    if not math.isfinite(a) or not math.isfinite(b):
        raise ValueError("ULP diagnostic requires finite operands")
    def ordered(x):
        value = struct.unpack(">Q", struct.pack(">d", float(x)))[0]
        return (~value & 0xFFFFFFFFFFFFFFFF) if value >> 63 else value | (1 << 63)
    return abs(ordered(a) - ordered(b))


def decimal_dot(a, b) -> float:
    with localcontext() as ctx:
        ctx.prec = 100
        result = sum(
            (Decimal.from_float(float(x)) * Decimal.from_float(float(y))
             for x, y in zip(a, b)), Decimal(0)
        )
        return float(result)


def decimal_norm(values) -> float:
    """High-precision sqrt(sum(exact binary64 squares)); informational."""
    with localcontext() as ctx:
        ctx.prec = 100
        sq = sum((Decimal.from_float(float(v)) ** 2 for v in values), Decimal(0))
        return float(sq.sqrt())


def matvec_decimal(T: np.ndarray, g: np.ndarray) -> np.ndarray:
    if T.shape != (3, 3) or g.shape != (3,):
        raise ValueError("Only original frozen three-free-parameter state permitted")
    return np.array([-decimal_dot(T[i], g) for i in range(3)], dtype=np.float64)


def verify(root: Path) -> tuple[dict, dict, dict]:
    original = json.loads((root/"summary.json").read_bytes())
    comparison = json.loads((root/"comparison.json").read_bytes())
    if (str(original.get("github_run_id")) != RUN
            or original.get("candidate_sha") != CANDIDATE
            or original.get("raw_evidence_sha256") != SHA
            or original.get("source_run_id") != "41863441006"
            or original.get("status") !=
                "AUTHOR_SIDE_BFGS_STATE_RECONSTRUCTION_NOT_SCIENTIFIC_PASS_NOT_TIMED"):
        raise ValueError("Original archived CI SHA/scientific status identity changed")
    strip = {"github_run_id","candidate_sha","raw_evidence_sha256","raw_evidence_location"}
    if {k:v for k,v in original.items() if k not in strip} != comparison:
        raise ValueError("Original archived summary/comparison JSON no longer identical")
    raw = {}
    for file_name, sha in SHA.items():
        b = (root/file_name).read_bytes()
        if hashlib.sha256(b).hexdigest() != sha:
            raise ValueError(f"Original raw SHA256 mismatch: {file_name}")
        engine = file_name.split("_")[0]
        raw[engine] = json.loads(b)
        if (raw[engine].get("status") != "UNTIMED_PUBLIC_FIT_BFGS_STATE_EXPORTED"
                or raw[engine].get("schema") !=
                    f"perf01-subject7-bfgs-state-{engine}-v1"
                or raw[engine].get("frozen_hgfx_sha") !=
                    "4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27"
                or raw[engine].get("frozen_matlab_sha") !=
                    "2437f4dc241541072722a2695ddeca7b44d83dd3"
                or raw[engine].get("subject_index_zero_based") != 7
                or raw[engine].get("finite_slots") != 25
                or raw[engine].get("trials") != 128
                or raw[engine].get("ridders_min_steps") != 10):
            raise ValueError(f"Wrong original frozen {engine} public fit input")
    if (raw["hgfx"]["source_input_sha256"] != raw["matlab"]["source_input_sha256"]
            or raw["hgfx"]["source_config_sha256"] != raw["matlab"]["source_config_sha256"]):
        raise ValueError("Original fitted source data/config SHA cross-engine mismatch")
    return original, comparison, raw


def inspect_scalar(new: float, archived: float) -> dict:
    return {
        "current": float(new),
        "archived": float(archived),
        "current_bits": bits(new),
        "archived_bits": bits(archived),
        "exact_binary64_match": bool(bits(new) == bits(archived)),
        "ulps": ulp_distance(new, archived),
        "abs_diff": abs(float(new) - float(archived)),
    }


def run(root: Path) -> dict:
    summary, comparison, sources = verify(root)
    rows=[]
    for engine in ("hgfx","matlab"):
        raw = sources[engine]
        Ts = np.asarray(raw["iter_inverse_hessian"],dtype=np.float64)
        gradients = np.asarray(
            [p["grad"] for p in raw["ridders_recomputed_history"]],dtype=np.float64)
        if Ts.shape != (N,3,3) or gradients.shape != (25,3):
            raise ValueError(f"{engine}: saved full matrix/gradient inventory changed")
        if not (np.isfinite(Ts).all() and np.isfinite(gradients).all()):
            raise ValueError(f"{engine}: nonfinite original BFGS inputs")
        for i in range(N):
            T,g=Ts[i],gradients[i]
            d=-(T@g)
            d_exact=matvec_decimal(T,g)
            original=comparison["line_search_candidates"][i][engine]
            current_norm=float(np.linalg.norm(d))
            current_slope=float(np.dot(g,d))
            archived_norm=float(original["raw_direction_norm"])
            archived_slope=float(original["gradient_dot_unclipped_direction"])
            if not (math.isfinite(current_norm) and math.isfinite(current_slope)):
                raise ValueError(f"{engine} nonfinite rederived scalar record {i}")
            rows.append({
                "engine":engine, "record_index_zero_based":i,
                "source_archived_status":original["status"],
                "source_archived_half_step_exponent":original.get("best_half_step_exponent"),
                "numpy_norm_vs_archived":inspect_scalar(current_norm,archived_norm),
                "numpy_slope_vs_archived":inspect_scalar(current_slope,archived_slope),
                "decimal_norm_of_current_matvec":decimal_norm(d),
                "math_hypot_norm_of_current_matvec":float(math.hypot(*d)),
                "decimal_slope_of_current_matvec":decimal_dot(g,d),
                "decimal_slope_of_decimal_matvec":decimal_dot(g,d_exact),
                "numpy_raw_direction":d.tolist(),
                "decimal_raw_direction":d_exact.tolist(),
                "numpy_vs_decimal_matvec_coordinate_ulps":
                    [ulp_distance(a,b) for a,b in zip(d,d_exact)],
            })
    cfg=io.StringIO()
    # Capture build diagnostics without assuming a 'file' argument.
    import contextlib
    with contextlib.redirect_stdout(cfg):
        np.show_config()
    feature={}
    try:
        feature={k:bool(v) for k,v in
                 np._core._multiarray_umath.__cpu_features__.items()}
    except (AttributeError,TypeError):
        pass
    pools=[]
    try:
        from threadpoolctl import threadpool_info
        pools=[{"internal_api":p.get("internal_api"),
                "thread_count":p.get("num_threads"),
                "architecture":p.get("architecture"),
                "version":p.get("version"),
                "filepath_basename":Path(str(p.get("filepath",""))).name}
               for p in threadpool_info()]
    except ImportError:
        pools=[]
    cpu_model=None
    cpuinfo=Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(errors="replace").splitlines():
            if line.lower().startswith("model name"):
                cpu_model=line.partition(":")[2].strip()
                break
    mismatch_norm=[r for r in rows if not r["numpy_norm_vs_archived"]["exact_binary64_match"]]
    mismatch_slope=[r for r in rows if not r["numpy_slope_vs_archived"]["exact_binary64_match"]]
    return {
        "schema":"perf01d-issue90-host-binary64-ulp-audit-v1",
        "status":STATUS,
        "original_bfgs_run":RUN,
        "original_bfgs_candidate_sha":CANDIDATE,
        "original_bfgs_raw_sha256":SHA,
        "original_fitting_science":"63/64 non-PASS, subject index 7 traj.mu/traj.muhat",
        "runtime":{
            "platform":platform.platform(),
            "system":platform.system(),
            "machine":platform.machine(),
            "processor":platform.processor(),
            "linux_cpu_model":cpu_model,
            "python":sys.version,
            "numpy":np.__version__,
            "numpy_build":cfg.getvalue(),
            "numpy_cpu_features":feature,
            "thread_pools":pools,
            "environment":{name:os.environ.get(name) for name in
                ("OPENBLAS_CORETYPE","OPENBLAS_NUM_THREADS","OMP_NUM_THREADS",
                 "MKL_NUM_THREADS","RUNNER_OS","GITHUB_RUN_ID","GITHUB_SHA")},
        },
        "total_original_engine_history_rows":len(rows),
        "archived_numpy_norm_ulp_mismatches":len(mismatch_norm),
        "archived_numpy_slope_ulp_mismatches":len(mismatch_slope),
        "max_norm_ulp_distance":max(r["numpy_norm_vs_archived"]["ulps"] for r in rows),
        "max_slope_ulp_distance":max(r["numpy_slope_vs_archived"]["ulps"] for r in rows),
        "rows":rows,
        "limitations":[
            "Cross-host scalar/BLAS differences are measured, not accepted as scientific parity.",
            "Decimal diagnostic uses exact binary64 operands, products and a high-precision square root; it is NOT the historical MATLAB/HGFX runtime algorithm.",
            "The original public fit and all fitting scientific thresholds, failures, denominators and frozen sources remain unchanged.",
            "These are operations on saved previously divergent optimization states, not a causal optimizer bug isolation.",
            "This run performs no optimization, timing, GPU validation or independent review.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=run(a.archive)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({
        "status":report["status"],
        "platform":report["runtime"]["platform"],
        "numpy":report["runtime"]["numpy"],
        "norm_ulp_mismatches":report["archived_numpy_norm_ulp_mismatches"],
        "slope_ulp_mismatches":report["archived_numpy_slope_ulp_mismatches"],
        "max_norm_ulps":report["max_norm_ulp_distance"],
        "max_slope_ulps":report["max_slope_ulp_distance"],
        "record_zero_hgfx":report["rows"][0],
        "rows":report["total_original_engine_history_rows"],
    },sort_keys=True))


if __name__=="__main__":
    main()
