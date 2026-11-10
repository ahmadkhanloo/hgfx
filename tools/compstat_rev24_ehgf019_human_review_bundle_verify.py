#!/usr/bin/env python3
"""Offline REV-2.4 eHGF-019 human-review packet verifier (stdlib only).

Verifies archived ZIPs, exact frozen old/dev/MATLAB source blobs, and the
original first finite-state mismatch. Does NOT run HGF, JAX, MATLAB, fitting,
objectives, or claim that the development patch scientifically passes.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parent
ORIGINAL="faebd113e9ee050a2490d08e1d1fbc54ba589becd1015d41cab4e7879a785b1c"
TRACE="a115cc946ddbe3504050e8a1720f50c0a1eb244a89a41a3ed33a9c971ab520e1"
DERIVED="db61cebae88dc5a408e1bf4c8955a13fe1fa0695fdc40d4b658e9497293e58be"
CASE_SHA="276d21f43a91fc8748438aafc6ec44f759f23dc2ae97dae8b4cc1274aba3fefb"
ARTIFACTS={
 "evidence/panel_g_original_synthetic.zip":ORIGINAL,
 "evidence/ehgf019_original_raw_trace.zip":TRACE,
 "evidence/ehgf019_read_only_derived_comparison.zip":DERIVED,
}
MEMBERS={
 "manifest.json":"59d86cb1687944841b802a2d6f4d4f9e2851eb59ba28abf9edbf332668718cec",
 "matlab.json":"54df9fd43c1044f6a7dd6d2c485a9bd76c8da7757d1dee276a4003f31d5b2397",
 "hgfx.json":"70fd09db1efac4d8d4df2e441525216850d302bd9cd0ee315f5681597c701503",
 "comparison.json":"cfd0c7e9f66890c2873706b77518a721119b725a04393ad99ef71e573c780430",
}
SOURCE_BLOBS={
 "source/matlab_hgf_volatility_update.m":"f5f50a160397de94f5f11545fdce4d74db6ca27b",
 "source/hgfx_v1_0_0_volatility.py":"afdbdcb5b4ae15926a7526cc604f6ca8f6fe7a76",
 "source/hgfx_dev_1_1_0b1_volatility.py":"07f70bba0df945c6be8b378a5d0db63a0f4e9a18",
}
def check(ok,explain):
 if not ok:raise ValueError(explain)
def hash256(data):
 return hashlib.sha256(data).hexdigest()
def git_blob(data):
 return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def parse_zip(name,expected,member_hashes):
 data=(ROOT/name).read_bytes()
 check(hash256(data)==expected,f"Unexpected frozen ZIP SHA256: {name}")
 with zipfile.ZipFile(ROOT/name) as z:
  check(set(z.namelist())==set(member_hashes),f"Archive member drift: {name}")
  blobs={}
  for key,expected_hash in member_hashes.items():
   content=z.read(key)
   check(hash256(content)==expected_hash,f"Archive member drift: {name}/{key}")
   blobs[key]=json.loads(content)
 return blobs
def classification(value):
 if type(value) in (int,float):
  check(math.isfinite(value),"Nonfinite raw JSON number must be IEEE string")
  return "FINITE"
 check(value in ("NaN","+Inf","-Inf"),"Unsupported nonfinite status")
 return value
def main():
 checks=(ROOT/"SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
 seen=set()
 for line in checks:
  digest,rel=line.split("  ",1)
  check(rel not in seen and ".." not in Path(rel).parts,"Unsafe/duplicate checksum")
  seen.add(rel)
  check(hash256((ROOT/rel).read_bytes())==digest,f"Packet checksum mismatch {rel}")
 actual={str(path.relative_to(ROOT)).replace("\\","/") for path in ROOT.rglob("*")
         if path.is_file() and path.name!="SHA256SUMS.txt"}
 check(actual==seen,"Unlisted or missing files in packet")
 print("PACKET SHA-256:",len(seen),"files PASS")
 for file,expected in ARTIFACTS.items():
  check(hash256((ROOT/file).read_bytes())==expected,"ZIP digest mismatch: "+file)
 print("ARTIFACT ZIPs 3/3 PASS")
 for file,expected in SOURCE_BLOBS.items():
  check(git_blob((ROOT/file).read_bytes())==expected,
        "Frozen source Git blob mismatch: "+file)
 print("SOURCE Git blobs 3/3 PASS")
 original=parse_zip("evidence/panel_g_original_synthetic.zip",ORIGINAL,MEMBERS)
 manifest=original["manifest.json"]
 check(manifest["manifest_sha256"]=="35e7c766d3f63cb53aa407c2e6563a34b1a5fd795b982d147475e4c3d409ea95",
       "Original manifest changed")
 groups=manifest["strata"]
 check(len(groups)==3 and all(len(g["rows"])==200 for g in groups),
       "Original 600 source cases changed")
 case=groups[1]["rows"][19]
 check(case["case_id"]=="REV24-G-ehgf_binary-019" and
       case["case_sha256"]==CASE_SHA,
       "Original failure case identity changed")
 traces=parse_zip("evidence/ehgf019_original_raw_trace.zip",TRACE,{
    "hgfx_trace.json":"c346f54572c396a9d9b2ea29e40b726edab1de4152251bfbc1cddf0a3c007ff2",
    "matlab_trace.json":"9d96afb97ff2a516a2a224c2f52aa7a3c5675e3b0a877fd0c602f0c21a639354",
 })
 derived=parse_zip("evidence/ehgf019_read_only_derived_comparison.zip",DERIVED,{
    "diagnostic_comparison.json":"0dc6b7db011d79a0b5a7434aaf3311776eab84ae0c800077604d53ac3fe45fa4",
 })["diagnostic_comparison.json"]
 ml=traces["matlab_trace.json"]
 hg=traces["hgfx_trace.json"]
 check(ml["source"]=="matlab" and hg["source"]=="hgfx" and
       ml["source_case_sha256"]==hg["source_case_sha256"]==CASE_SHA,
       "Trace case identity changed")
 check(ml["matlab_version"]=="26.2.0.3433840 (R2026b) Update 1",
       "MATLAB reference runtime version drift")
 flat=ml["inferred_states"]["sa"]
 rows=hg["inferred_states"]["sa"]
 check(len(flat)==384 and len(rows)==128 and all(len(row)==3 for row in rows),
       "Original MATLAB cell layout or HGFX trajectory shape changed")
 changes=[]
 for t in range(128):
  for level in range(3):
   x=flat[level*128+t]
   y=rows[t][level]
   if classification(x)!=classification(y):
    changes.append((t,level,x,y))
 check(changes and changes[0]==(8,2,8.209456713045242,"NaN"),
       "Expected original trial-8 level-3 variance divergence not found")
 llm=ml["trial_log_likelihoods"]
 llh=hg["trial_log_likelihoods"]
 check(len(llm)==len(llh)==128,"Original likelihood horizon drift")
 loss=[t for t in range(128)
       if classification(llm[t])!=classification(llh[t])]
 check(loss and loss[0]==11,
       "Original trial-11 likelihood-status divergence not found")
 first=derived["first_finite_status_difference"]
 check(first["location"]=="inferred_states.sa"
       and first["trial_zero_based"]==8 and first["level_zero_based"]==2,
       "Derived comparison first-divergence report changed")
 check(derived["causal_expression_and_mechanism"]=="NOT_ESTABLISHED"
       and derived["scientific_gate"]=="NOT_GLOBAL_PASS",
       "An unsupported scientific PASS was asserted")
 print("ORIGINAL PAIR: first exported status divergence trial 8, level 3, sa")
 print("ORIGINAL PAIR: first trial likelihood status divergence trial 11")
 print("LIMITATION: causal intermediate values reconstructed, not directly measured")
 print("NO HUMAN REVIEW PROVIDED. NO FIXED DEV SCIENTIFIC OR GLOBAL PARITY PASS.")


if __name__=="__main__":
 main()
