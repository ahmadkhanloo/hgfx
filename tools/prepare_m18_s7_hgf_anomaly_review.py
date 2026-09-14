#!/usr/bin/env python3
"""Prepare exact immutable S7 HGF anomaly cases for diagnostic review.

The two positional manifest arguments are regenerated-current-head manifests and
are recorded only as non-authoritative diagnostics. Scientific data are loaded
exclusively from the committed fixture copied from the first complete S7 run.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from hgfx.diagnostics.recovery import fit_binary_variant
from hgfx.optim.compat_quasinewton import QuasiNewtonOptions

PROTOCOL="m18-s7-hgf-anomaly-review-1"
FIXTURE_PROTOCOL="m18-s7-hgf-anomaly-fixture-1"
REFERENCE_COMMIT="2437f4dc241541072722a2695ddeca7b44d83dd3"
FIXTURE_PATH=Path("reference/validation/m18_s7_paired_recovery/hgf_anomaly_fixture.json")
FIXTURE_SHA256="b2893c19b504089268bd38b34eea014ae1d1777fdefc98e589f9e6381e9a841e"
EXPECTED={
"PR-hgf_binary-T128-S0.15-R3":{"case_sha256":"e13c5efe72b43d951ed0ff6359b2f604cbd5bc8e4e333edfcc2519fba3b71fc0","matlab_final":[-2.6150892895331053,-5.993242057216259,4.463011892389776],"matlab_negLj":6.622752693490324,"matlab_converged":False,"hgfx_final":[-2.615089289536023,-5.9932420572065235,4.46301189238864],"hgfx_negLj":6.6227526934902885,"hgfx_converged":True},
"PR-hgf_binary-T256-S0.35-R0":{"case_sha256":"1b99d57ab00960941d6d0e2997712bfc5b3319edcd2521fee257a89b7ccec8b5","matlab_final":[-1.681508358629877,-2.813834229811849,4.040575231980671],"matlab_negLj":13.292404684084028,"matlab_converged":True,"hgfx_final":[-1.6832085839490636,-2.807283698305754,4.053638499739679],"hgfx_negLj":13.294859618272989,"hgfx_converged":False},
"PR-hgf_binary-T256-S0.35-R4":{"case_sha256":"b2aeadf32705ff8cbbf90737611cf059d59f853b82ca44605dd6afe906e2aeca","matlab_final":[-1.729182054270742,-3.756995925956133,4.224706350948065],"matlab_negLj":11.790436615859958,"matlab_converged":False,"hgfx_final":[-1.7009824622040677,-5.037546349956735,4.208519462142309],"hgfx_negLj":11.961671424898556,"hgfx_converged":False},
}

def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def current_manifest_note(path:Path)->dict:
    d=json.loads(path.read_text())
    return {"file_sha256":sha(path),"shard_sha256":d.get("shard_sha256"),"note":"NON_AUTHORITATIVE_CURRENT_HEAD_REGENERATION"}

def main(man128:Path,man256:Path,out:Path)->int:
    if sha(FIXTURE_PATH)!=FIXTURE_SHA256: raise ValueError("Frozen anomaly fixture byte hash mismatch")
    f=json.loads(FIXTURE_PATH.read_text())
    if f.get("protocol")!=FIXTURE_PROTOCOL or f.get("parent_protocol")!="m18-s7-paired-recovery-1": raise ValueError("Fixture protocol mismatch")
    if f.get("reference_commit")!=REFERENCE_COMMIT or f.get("source_run")!=34856542785: raise ValueError("Fixture provenance mismatch")
    by={c["case_id"]:c for c in f.get("cases",[])}
    if set(by)!=set(EXPECTED): raise ValueError("Frozen anomaly case set mismatch")
    cases=[]
    for cid,e in EXPECTED.items():
        c=by[cid]
        if c.get("case_sha256")!=e["case_sha256"]: raise ValueError(f"Case hash mismatch for {cid}")
        if c.get("model")!="hgf_binary" or [int(x) for x in c.get("free_indices_zero_based",[])]!=[12,13,14]: raise ValueError(f"Case contract mismatch for {cid}")
        u=np.asarray(c["u"],dtype=np.float64); y=np.asarray(c["y"],dtype=np.float64)
        if len(u)!=int(c["trial_count"]) or len(y)!=int(c["trial_count"]): raise ValueError(f"Case length mismatch for {cid}")
        fit=fit_binary_variant(y,u,"hgf_binary",options=QuasiNewtonOptions(max_iter=100))
        current={"final_free":fit.final_free.tolist(),"negLj":float(fit.objective.neg_log_joint),"termination":fit.optimizer.termination,"converged":fit.optimizer.termination in {"tol_arg","tol_grad"},"initial_free":fit.initial_full[np.asarray(fit.free_indices,dtype=np.int64)].tolist(),"free_indices_zero_based":list(fit.free_indices)}
        cases.append({**c,"expected_s7":e,"current_hgfx":current})
    payload={"protocol":PROTOCOL,"parent_protocol":"m18-s7-paired-recovery-1","reference_commit":REFERENCE_COMMIT,"fixture_sha256":FIXTURE_SHA256,"source_run":f["source_run"],"source_head":f["source_head"],"source_artifacts":f["source_artifacts"],"non_authoritative_regeneration":{"hgf-t128-s015":current_manifest_note(man128),"hgf-t256-s035":current_manifest_note(man256)},"existing_gate":{"rtol":3e-8,"atol":3e-10},"cases":cases,"acceptance_effect":"NONE_DIAGNOSTIC_ONLY"}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"protocol":PROTOCOL,"fixture_sha256":FIXTURE_SHA256,"cases":list(EXPECTED)}))
    return 0
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("manifest_128",type=Path); p.add_argument("manifest_256",type=Path); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); raise SystemExit(main(a.manifest_128,a.manifest_256,a.output))
