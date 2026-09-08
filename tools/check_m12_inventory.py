from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    prefix: str
    family: str
    status: str
    evidence: str
    reason: str


PERCEPTUAL_RULES = (
    Rule("hgf_ar1_binary_mab", "AR1 binary MAB (HGF)", "REFERENCE_ONLY", "M12", "multi-armed-bandit tensor/reward semantics require a dedicated fixture/API"),
    Rule("ehgf_ar1_binary_mab", "AR1 binary MAB (eHGF)", "REFERENCE_ONLY", "M12", "multi-armed-bandit tensor/reward semantics require a dedicated fixture/API"),
    Rule("uhgf_ar1_binary_mab", "AR1 binary MAB (uHGF)", "REFERENCE_ONLY", "M12", "multi-armed-bandit tensor/reward semantics require a dedicated fixture/API"),
    Rule("hgf_binary_mab", "binary MAB", "REFERENCE_ONLY", "M12", "multi-arm state tensors and reward-coded inputs are outside the frozen core compatibility slice"),
    Rule("hgf_ar1_mab", "continuous AR1 MAB", "REFERENCE_ONLY", "M12", "multi-arm continuous state tensors need a dedicated compatibility API"),
    Rule("hgf_ar1_binary", "AR1 binary HGF", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("ehgf_ar1_binary", "AR1 binary eHGF", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("uhgf_ar1_binary", "AR1 binary uHGF", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("hgf_ar1", "continuous AR1 HGF", "REFERENCE_ONLY", "M12", "continuous AR1 was not required by the P1 binary specialized gate and has a distinct parameter layout"),
    Rule("hgf_binary_pu_tbt", "binary PU-TBT HGF", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("ehgf_binary_pu_tbt", "binary PU-TBT eHGF", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("uhgf_binary_pu_tbt", "binary PU-TBT uHGF", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("hgf_binary_pu", "binary PU HGF", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("ehgf_binary_pu", "binary PU eHGF", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("uhgf_binary_pu", "binary PU uHGF", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("hgf_jget", "JGET HGF", "REFERENCE_ONLY", "M12", "specialized JGET state recursion and parameterization require a dedicated scientific fixture"),
    Rule("ehgf_jget", "JGET eHGF", "REFERENCE_ONLY", "M12", "specialized JGET state recursion and parameterization require a dedicated scientific fixture"),
    Rule("uhgf_jget", "JGET uHGF", "REFERENCE_ONLY", "M12", "specialized JGET state recursion and parameterization require a dedicated scientific fixture"),
    Rule("hgf_categorical_norm", "categorical normalized HGF", "REFERENCE_ONLY", "M12", "multinomial tensor recursion is isolated from the binary/continuous compatibility core"),
    Rule("hgf_categorical", "categorical HGF", "REFERENCE_ONLY", "M12", "multinomial tensor recursion is isolated from the binary/continuous compatibility core"),
    Rule("hgf_whatworld", "WhatWorld HGF", "REFERENCE_ONLY", "M12", "high-dimensional transition/world latent-state semantics need dedicated fixtures"),
    Rule("hgf_whichworld", "WhichWorld HGF", "REFERENCE_ONLY", "M12", "world-mixture latent-state semantics need dedicated fixtures"),
    Rule("rw_binary_dual", "dual Rescorla-Wagner", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("rw_binary", "Rescorla-Wagner", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("ph_binary", "Pearce-Hall", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("sutton_k1_binary", "Sutton K1", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("tapas_kf", "scalar Kalman filter", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("tapas_hmm", "HMM", "DONE", "M12", "MATLAB/Python forward oracle"),
    Rule("tapas_hhmm", "HHMM", "REFERENCE_ONLY", "M12", "frozen file declares htapas_hmm inside tapas_hhmm.m and uses tree flattening semantics requiring source repair/fixture before port"),
    Rule("bayes_optimal", "Bayes-optimal auxiliary families", "REFERENCE_ONLY", "M12", "stored in perceptual/ but implement auxiliary likelihoods rather than a standalone latent-state recursion"),
    Rule("rs_", "response-surprise auxiliary models", "REFERENCE_ONLY", "M12", "auxiliary surprise/belief/precision models are retained as reference-only analysis models"),
    Rule("squared_pe", "squared prediction-error auxiliary", "REFERENCE_ONLY", "M12", "auxiliary deterministic analysis model; not part of the compatibility forward core"),
    Rule("hgf_binary", "standard binary HGF", "DONE", "M4", "golden forward parity"),
    Rule("ehgf_binary", "standard binary eHGF", "DONE", "M5", "golden forward parity"),
    Rule("uhgf_binary", "standard binary uHGF", "DONE", "M6", "golden forward parity"),
    Rule("hgf_", "standard continuous HGF support files", "DONE", "M4", "golden continuous forward parity"),
    Rule("ehgf", "standard continuous eHGF", "DONE", "M5", "golden continuous forward parity"),
    Rule("uhgf", "standard continuous uHGF", "DONE", "M6", "golden continuous forward parity"),
)

OBSERVATION_RULES = (
    Rule("condhalluc_obs", "conditional hallucination observations", "REFERENCE_ONLY", "M12", "P2 family coupled to specialized conditional-hallucination perceptual integrations"),
    Rule("logrt_linear_whatworld", "WhatWorld logRT", "REFERENCE_ONLY", "M12", "depends on reference-only WhatWorld state layout"),
    Rule("softmax_mu3_wld", "world mu3 softmax", "REFERENCE_ONLY", "M12", "depends on reference-only world state layout"),
    Rule("softmax_wld", "world softmax", "REFERENCE_ONLY", "M12", "depends on reference-only world state layout"),
    Rule("beta_obs", "beta observation", "DONE", "M7", "P1 observation parity"),
    Rule("cdfgaussian_obs", "CDF Gaussian observation", "DONE", "M7", "P1 observation parity"),
    Rule("gaussian_obs", "Gaussian observations", "DONE", "M7", "P1 observation parity"),
    Rule("logrt_linear_binary", "binary logRT observations", "DONE", "M7", "P1 observation parity"),
    Rule("softmax_2beta", "two-beta softmax", "DONE", "M7", "P1 observation parity"),
    Rule("softmax_binary", "binary softmax", "DONE", "M7", "P0 observation parity"),
    Rule("softmax_mu3", "mu3 softmax", "DONE", "M7", "P1 observation parity"),
    Rule("softmax", "categorical softmax", "DONE", "M7", "P1 observation parity"),
    Rule("unitsq_sgm_mu3", "mu3 unit-square sigmoid", "DONE", "M7", "P1 observation parity"),
    Rule("unitsq_sgm", "unit-square sigmoid", "DONE", "M7", "P0 observation parity"),
)


def classify(filename: str, rules: tuple[Rule, ...]) -> Rule | None:
    matches = [rule for rule in rules if filename.startswith(rule.prefix)]
    if not matches:
        return None
    # Rules are ordered most-specific first. Enforce that convention explicitly.
    return matches[0]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "reference" / "matlab_manifest.tsv"
    paths = [line.split("\t", 1)[0] for line in manifest.read_text(encoding="utf-8").splitlines() if line]

    unresolved: list[str] = []
    counts = {"DONE": 0, "REFERENCE_ONLY": 0}
    family_status: dict[tuple[str, str], Rule] = {}

    for path in paths:
        if path.startswith("perceptual/"):
            filename = path.removeprefix("perceptual/")
            rule = classify(filename, PERCEPTUAL_RULES)
        elif path.startswith("observation/"):
            filename = path.removeprefix("observation/")
            rule = classify(filename, OBSERVATION_RULES)
        else:
            continue
        if rule is None:
            unresolved.append(path)
            continue
        counts[rule.status] += 1
        family_status[(rule.family, rule.status)] = rule

    if unresolved:
        raise AssertionError("Unclassified frozen model files:\n" + "\n".join(unresolved))

    invalid = [rule for rule in family_status.values() if rule.status not in {"DONE", "REFERENCE_ONLY"}]
    if invalid:
        raise AssertionError(f"Invalid M12 family statuses: {invalid}")

    done_families = sum(1 for _, status in family_status if status == "DONE")
    ref_families = sum(1 for _, status in family_status if status == "REFERENCE_ONLY")
    print(
        "M12 inventory classification: PASS "
        f"(DONE files={counts['DONE']}, REFERENCE_ONLY files={counts['REFERENCE_ONLY']}, "
        f"DONE families={done_families}, REFERENCE_ONLY families={ref_families})"
    )


if __name__ == "__main__":
    main()
