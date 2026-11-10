#!/usr/bin/env python3
"""Offline independent evidence packet validation for REV-2.4.

STD-LIB ONLY. No MATLAB or HGFX evaluations are performed.
Recounts original synthetic Panel G and the SANITIZED Panel E summary.
The private historical Panel E raw archive provenance is NOT verified here.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import sys
import zipfile

G_ZIP_SHA="faebd113e9ee050a2490d08e1d1fbc54ba589becd1015d41cab4e7879a785b1c"
E_ZIP_SHA="41e2aca61afb0d1961c653b87db3b36a1edd204f7b68ee0b362c958474fb96bb"
B_ZIP_SHA="faeae69aefffa00be28dbeade9371c5e0df85c784d64ff8d2961640d4ca09c4c"
EXPECTED_G_MEMBER_SHA={
 "manifest.json":"59d86cb1687944841b802a2d6f4d4f9e2851eb59ba28abf9edbf332668718cec",
 "hgfx.json":"70fd09db1efac4d8d4df2e441525216850d302bd9cd0ee315f5681597c701503",
 "matlab.json":"54df9fd43c1044f6a7dd6d2c485a9bd76c8da7757d1dee276a4003f31d5b2397",
 "comparison.json":"cfd0c7e9f66890c2873706b77518a721119b725a04393ad99ef71e573c780430",
}
EXPECTED_E_MEMBER_SHA={
 "input_source_audit.json":"fad8d25354ea0a367fb901fe7c4111db4a4e3390274494269662e8755001890d",
 "panel_e_comparison.json":"051aea43a11f7788b85d64a9cb8e82a59a274a70aa347f1927920d991a8ce86d",
}
EXPECTED_B_MEMBER_SHA={
 "endpoint_gap_bounds.json":"e0dae861801721d33e2f219c73fcc8694621968d028befc198baa483faab9caf",
}
PROTOCOL="compstat-rev2-4-objective-cross-eval-v1"
HGF_ATOL=2e-13
HGF_RTOL=2e-11


def require(condition,message):
 if not condition:raise AssertionError(message)


def sha256(raw):
 return hashlib.sha256(raw).hexdigest()


def canonical_hash(doc):
 return sha256(json.dumps(doc,sort_keys=True,separators=(",",":"),
                          allow_nan=False).encode("utf-8"))


def verify_file_hashes(root):
 checks=root/"SHA256SUMS.txt"
 require(checks.is_file(),"Missing packet SHA256SUMS.txt")
 lines=checks.read_text(encoding="utf-8").splitlines()
 seen=set()
 for line in lines:
  digest,rel=line.split("  ",1)
  require(rel not in seen and ".." not in Path(rel).parts,"Unsafe/duplicate checksum path")
  seen.add(rel)
  full=root/rel
  require(full.is_file(),f"Missing packet file {rel}")
  require(sha256(full.read_bytes())==digest,f"Checksum mismatch {rel}")
 require(len(seen)>=15,"Reviewer evidence packet unexpectedly incomplete")
 discovered={str(p.relative_to(root)).replace("\\","/")
             for p in root.rglob("*") if p.is_file() and
             p.name!="SHA256SUMS.txt"}
 require(discovered==seen,
         f"Unlisted packet files {sorted(discovered-seen)}; missing {sorted(seen-discovered)}")
 print("INTEGRITY: PASS — all",len(seen),"listed files present and matching")


def source_zip(root,filename,digest,members):
 path=root/"evidence"/filename
 require(sha256(path.read_bytes())==digest,f"Original artifact ZIP hash mismatch: {filename}")
 with zipfile.ZipFile(path) as z:
  names=set(z.namelist())
  require(names==set(members),
          f"Unexpected original archive member set in {filename}")
  docs={}
  for member,member_hash in members.items():
   data=z.read(member)
   require(sha256(data)==member_hash,f"Archived member checksum mismatch {member}")
   docs[member]=json.loads(data)
 return docs


def finite(value):
 return (type(value) in (int,float)) and math.isfinite(value)


def counts_original_g(g):
 manifest,ma,ha,cmp=(g[x] for x in ("manifest.json","matlab.json","hgfx.json",
                                     "comparison.json"))
 require(manifest["protocol"]==PROTOCOL and cmp["protocol"]==PROTOCOL,"Wrong original G protocol")
 check_hash=canonical_hash({k:v for k,v in manifest.items() if k!="manifest_sha256"})
 require(check_hash==manifest["manifest_sha256"]==
         "35e7c766d3f63cb53aa407c2e6563a34b1a5fd795b982d147475e4c3d409ea95",
         "Original manifest semantic hash mismatch")
 require(manifest["n_per_model"]==200 and len(manifest["strata"])==3,"Original grid changed")
 require(len(ma["cases"])==len(ha["cases"])==len(cmp["cases"])==600,"G denominator lost")
 require(cmp["scientific_gate"]=="NOT_GLOBAL_PASS","Global PASS unexpectedly asserted")
 stats=Counter()
 hgf_pass=0
 one_sided=[]
 for i,(mr,hr,record) in enumerate(zip(ma["cases"],ha["cases"],cmp["cases"])):
  for source,row in (("matlab",mr),("hgfx",hr)):
   require(row["source"]==source if "source" in row else True,"Incorrect G source")
   require(isinstance(row["valid"],bool),f"G case {i}: missing source validity")
   require(row["case_id"]==record["case_id"] and
           row["case_sha256"]==record["case_sha256"],
           f"G case {i}: source hash/order mismatch")
  model=record["model"]
  require(model in ("hgf_binary","ehgf_binary","uhgf_binary"),"Wrong G family")
  stats[model+":all"]+=1
  if mr["valid"] and hr["valid"]:
   stats["both_valid"]+=1
   if model=="hgf_binary":
    for field in ("neg_log_joint","neg_log_likelihood","log_likelihood"):
     a,b=mr[field],hr[field]
     require(finite(a) and finite(b),"G valid HGF field nonfinite")
     require(abs(a-b)<=HGF_ATOL+HGF_RTOL*abs(a),
             f"HGF objective field fails frozen gate at {i}:{field}")
    a,b=mr["trial_log_likelihoods"],hr["trial_log_likelihoods"]
    require(len(a)==len(b)==128,"G HGF trial count lost")
    require(all(finite(x) and finite(y) and
                abs(x-y)<=HGF_ATOL+HGF_RTOL*abs(x)
                for x,y in zip(a,b)),"HGF trial likelihood outside gate")
    hgf_pass+=1
  elif not mr["valid"] and not hr["valid"]:
   stats["both_invalid"]+=1
  else:
   stats["one_sided_invalid"]+=1
   one_sided.append(record["case_id"])
 require([stats["hgf_binary:all"],stats["ehgf_binary:all"],stats["uhgf_binary:all"]]==[200]*3,
         "G grid family denominator changed")
 require((stats["both_valid"],stats["both_invalid"],stats["one_sided_invalid"])==
         (560,39,1),"G published validity counts not reproducible")
 require(one_sided==["REV24-G-ehgf_binary-019"],"Original 019 asymmetric identity changed")
 require(hgf_pass==164,"Only 164 HGF both-valid objective evaluations satisfy M8")
 print("PANEL G: SOURCE NUMERIC RECOUNT PASS — 600 total; 560 both-valid; 39 jointly invalid;"
       " 1 asymmetric; 164 HGF both-valid within frozen M8 criterion")


def counts_sanitized_e(e):
 require(e["protocol"]==PROTOCOL and e["panel"]=="E","Wrong Panel E protocol")
 require(e["scientific_gate"]=="NOT_GLOBAL_PASS"
         and e["case_denominator"]==66 and e["endpoint_slot_denominator"]==132,
         "Panel E original denominator or status changed")
 rows=e["cases"]
 require(len(rows)==132,"Panel E incomplete")
 both=sum(r["matlab_valid"] and r["hgfx_valid"] for r in rows)
 missing=[r for r in rows if r["classification"]=="INSUFFICIENT_REFERENCE_EVIDENCE"]
 hgf=[r for r in rows if r["model"]=="hgf_binary"]
 require(both==131 and len(missing)==1
         and missing[0]["case_id"]=="D02_fit"
         and missing[0]["at_original_endpoint"]=="hgfx","Panel E case/missing status changed")
 require(len(hgf)==128 and all(r["classification"]=="SHARED_OBJECTIVE_WITHIN_EXISTING_GATE"
                                for r in hgf),"Panel E HGF M8 gate count mismatch")
 max_delta=max(r["objective_field_abs_differences"]["neg_log_joint"]["abs_difference"]
               for r in hgf)
 require(math.isclose(max_delta,2.842170943040401e-14,rel_tol=0,abs_tol=1e-18),
         "Panel E max negative-log-joint gap changed")
 require(all(not any(x in r for x in ("inputs","responses","endpoints","trial_log_likelihoods"))
             for r in rows),"Sanitized Panel E artifact leaks raw data")
 print("PANEL E: SANITIZED REPORT RECOUNT PASS — 131/132 matched, 128 HGF within original"
       " M8 gate; original HGFX D02 endpoint missing; RAW SOURCE NOT CHECKED")


def verify_posthoc(b,e):
 require(b["panel_e_comparison_sha256"]==EXPECTED_E_MEMBER_SHA["panel_e_comparison.json"],
         "Bounds not tied to original E comparator SHA")
 require(b["accepted_as_new_gate"] is False and b["science_execution"]=="NONE_NEW"
         and b["reported_panel_e_science_gate"]=="NOT_GLOBAL_PASS",
         "Posthoc bound mislabeled as prospective PASS")
 require(b["original_subjects"]==64 and
         b["missing_original_hgfx_endpoint"]==["D02_fit"],"Posthoc source denominator changed")
 v=b["cohort64"]["max_observed_cross_fit_objective_gap"]
 require(v["subject_zero_based"]==47 and
         math.isclose(v["value"],3.4023628359136637e-10,rel_tol=0,abs_tol=1e-20),
         "Posthoc cohort max changed")
 print("POSTHOC: REPORT METADATA PASS — 64 subjects; no re-evaluation; not a frozen gate")


def main():
 root=Path(__file__).resolve().parent
 verify_file_hashes(root)
 g=source_zip(root,"panel_g_original_artifact.zip",G_ZIP_SHA,EXPECTED_G_MEMBER_SHA)
 e=source_zip(root,"panel_e_sanitized_artifact.zip",E_ZIP_SHA,EXPECTED_E_MEMBER_SHA)
 b=source_zip(root,"panel_e_posthoc_bounds_artifact.zip",B_ZIP_SHA,EXPECTED_B_MEMBER_SHA)
 counts_original_g(g)
 counts_sanitized_e(e["panel_e_comparison.json"])
 verify_posthoc(b["endpoint_gap_bounds.json"],e["panel_e_comparison.json"])
 print("LIMITATION: NO INDEPENDENT RAW PANEL E ARCHIVE AUDIT. NO MATLAB RERUN."
       " NO SCIENTIFIC OR GLOBAL PARITY PASS. REVIEWER SIGN-OFF STILL REQUIRED.")


if __name__=="__main__":
 try:main()
 except Exception as exc:
  print("PACKET VALIDATION FAILED:",type(exc).__name__,str(exc),file=sys.stderr)
  raise SystemExit(1) from exc
