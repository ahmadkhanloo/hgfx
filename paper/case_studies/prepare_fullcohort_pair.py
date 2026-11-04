"""Prepare every original subject/block without inspecting numerical compatibility."""
from io import BytesIO
import hashlib, json, re, sys
from pathlib import Path
import numpy as np
from scipy.io import loadmat
from prepare_realdata_pair import CASES, get_source

EXPECTED = {"suthaharan_2021": (130, 260), "reed_2020": (33, 66)}
REGEX = {
 "suthaharan_2021": re.compile(r"^(TP\d+_V3)_choices_([12])$"),
 "reed_2020": re.compile(r"^(P\d+)_choices_(804020|905010)$"),
}

def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    rows=[]
    checks=[]
    for study, spec in CASES.items():
        data=loadmat(BytesIO(get_source(spec)),squeeze_me=False)
        pairs=[]
        for name in data:
            m=REGEX[study].fullmatch(name)
            if m:
                person,block=m.groups()
                pairs.append((person,block,person+"_outcomes_"+block,name))
        pairs.sort(key=lambda p:(int(re.search(r"\d+",p[0]).group()),p[1]))
        expected_people,expected_pairs=EXPECTED[study]
        actual_people=len({p[0] for p in pairs})
        checks.append({"study":study,"expected_people":expected_people,"actual_people":actual_people,
                       "expected_cases":expected_pairs,"actual_cases":len(pairs),
                       "sha256":spec["sha256"]})
        if (actual_people,len(pairs)) != (expected_people,expected_pairs):
            continue
        for i,(person,block,okey,ckey) in enumerate(pairs):
            key=f"{study}_{i+1:04d}"
            row={"id":key,"study":study,"original_variables":[okey,ckey],"trials":80}
            try:
                o=np.asarray(data[okey],dtype=np.float64)
                c=np.asarray(data[ckey],dtype=np.float64)
                if o.shape!=(80,1) or c.shape!=(80,1): raise ValueError("unexpected original shapes")
                u,y=o.ravel(),c.ravel()
                if not np.all(np.isin(u[np.isfinite(u)],[0,1])) or np.isinf(u).any():
                    raise ValueError("BLOCKED_DATA_CODING outcomes")
                if not np.all(np.isin(y[np.isfinite(y)],[1,2,3])) or np.isinf(y).any():
                    raise ValueError("BLOCKED_DATA_CODING choices")
                path=out/(key+"_input.txt")
                np.savetxt(path,np.column_stack((u,y)),fmt="%.17g")
                row.update(status="INPUT_READY",
                    ignored_trials=int(np.count_nonzero(np.isnan(u)|np.isnan(y))),
                    input_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            except Exception as e:
                row.update(status="BLOCKED_INPUT_SEMANTICS",reason=str(e)[:200])
            rows.append(row)
    manifest={"expected_total_cases":326,"actual_total_cases":len(rows),
              "status":"COHORT_SOURCE_INVENTORY_NOT_MODEL_PARITY","source_checks":checks,"cases":rows}
    (out/"all_cohort_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"source_checks":checks,"total_cases":len(rows),
        "blocked_cases":sum(c["status"]!="INPUT_READY" for c in rows)},indent=2))
    if len(rows)!=326: raise SystemExit("BLOCKED_UNEXPECTED_SOURCE_COHORT_SIZE")

if __name__=="__main__":
    main()
