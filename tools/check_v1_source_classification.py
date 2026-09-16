from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys


EXPECTED_MATLAB_FILES = 334
ALLOWED_STATUSES = {"DONE", "PLOT_ONLY", "DEPRECATED", "NOT_APPLICABLE"}


@dataclass(frozen=True)
class SourceClassification:
    path: str
    status: str
    evidence: str
    reason: str


def _load_m12_inventory():
    path = Path(__file__).with_name("check_m12_inventory.py")
    name = "_hgfx_check_m12_inventory"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


M12 = _load_m12_inventory()


UTILITY_CLASSIFICATIONS = {
    "align_priors.m": ("DONE", "M2 parameter/config parity", "prior-vector alignment semantics are implemented by immutable Python configs"),
    "align_priors_fields.m": ("DONE", "M2 parameter/config parity", "field-wise prior alignment semantics are covered by config construction"),
    "bayesian_parameter_average.m": ("DONE", "M18 D12 Bayesian Parameter Averaging", "public BPA compatibility surface has frozen MATLAB parity"),
    "boltzmann.m": ("DONE", "M3 scalar numerical parity", "reference Boltzmann semantics and edge behavior are covered"),
    "datagen_categorical.m": ("NOT_APPLICABLE", "M12 categorical model coverage", "non-scientific stochastic demo/input generator; HGFX categorical models accept explicit categorical inputs and do not claim MATLAB RNG identity"),
    "lambert_w0.m": ("DONE", "M3 scalar numerical parity", "reference Lambert W0 algorithm and edge behavior are covered"),
    "nearest_psd.m": ("DONE", "M3 scalar numerical parity", "nearest-PSD utility is implemented and validated"),
    "riddersdiff.m": ("DONE", "M10 Hessian/LME parity + M18 optimizer validation", "Ridders first-derivative compatibility utility is implemented in the fitting stack"),
    "riddersdiff2.m": ("DONE", "M10 Hessian/LME parity + M18 optimizer validation", "Ridders second-derivative compatibility utility is implemented in the fitting stack"),
    "riddersdiffcross.m": ("DONE", "M10 Hessian/LME parity + M18 optimizer validation", "Ridders cross-derivative compatibility utility is implemented in the fitting stack"),
    "riddersgradient.m": ("DONE", "M10 Hessian/LME parity + M18 optimizer validation", "Ridders gradient compatibility utility is implemented in the fitting stack"),
    "riddershessian.m": ("DONE", "M10 Hessian/LME parity + M18 optimizer validation", "Ridders Hessian compatibility utility is implemented and used by release validation"),
    "tapas_Cov2Corr.m": ("DONE", "M3 scalar numerical parity + D10 fit-correlation surface", "covariance-to-correlation semantics are implemented and surfaced in fit diagnostics"),
    "tapas_autocorr.m": ("DONE", "M18 D11 residual diagnostics", "frozen circular FFT/population-variance autocorrelation semantics are implemented"),
    "tapas_logit.m": ("DONE", "M3 scalar numerical parity", "logit transform is implemented and validated"),
    "tapas_sgm.m": ("DONE", "M3 scalar numerical parity", "sigmoid transform is implemented and validated"),
}


def _scientific_classification(path: str) -> SourceClassification:
    if path.startswith("perceptual/"):
        filename = path.removeprefix("perceptual/")
        rule = M12.classify(filename, M12.PERCEPTUAL_RULES)
    else:
        filename = path.removeprefix("observation/")
        rule = M12.classify(filename, M12.OBSERVATION_RULES)
    if rule is None:
        raise AssertionError(f"unclassified frozen scientific source: {path}")
    if rule.status != "DONE":
        raise AssertionError(f"scientific source is not DONE: {path} -> {rule.status}")
    return SourceClassification(path, "DONE", rule.evidence, rule.reason)


def classify_source(path: str) -> SourceClassification:
    if path.startswith(("perceptual/", "observation/")):
        return _scientific_classification(path)

    if path.startswith("building_blocks/"):
        return SourceClassification(path, "DONE", "M4 HGF Forward Parity", "frozen HGF building-block semantics are covered by golden forward parity")

    if path.startswith("core/"):
        return SourceClassification(path, "DONE", "M9-M11 + M18 D09/workflow closure", "fit, optimization, simulation and sampleModel compatibility surfaces are validated in their release gates")

    if path.startswith("demo/"):
        return SourceClassification(path, "DONE", "V1 Full MATLAB Demo Composition", "official MATLAB demo workflow is represented by the validated Python companion and composite oracle evidence")

    if path.startswith("_original_models/"):
        return SourceClassification(path, "DEPRECATED", "M12 complete model coverage", "upstream archival pre-unified model implementations; current scientific families are implemented and validated through the frozen v8 unified model surfaces")

    if path.startswith("plotting/"):
        evidence = "M18 D10/D11 analysis surfaces + model-specific forward parity"
        return SourceClassification(path, "PLOT_ONLY", evidence, "visualization source is non-scientific release surface; numerical data/trajectory surfaces are validated rather than pixel identity")

    if path.startswith("tests/"):
        return SourceClassification(path, "NOT_APPLICABLE", "HGFX golden/regression/oracle test suite", "upstream MATLAB test harness is reference evidence, not a runtime API; corresponding Python scientific behavior is covered by HGFX validation")

    if path.startswith("utilities/"):
        filename = path.removeprefix("utilities/")
        payload = UTILITY_CLASSIFICATIONS.get(filename)
        if payload is None:
            raise AssertionError(f"unclassified frozen utility source: {path}")
        status, evidence, reason = payload
        return SourceClassification(path, status, evidence, reason)

    if path == "setup.m":
        return SourceClassification(path, "NOT_APPLICABLE", "Python packaging / S10 clean-wheel release readiness", "MATLAB path/bootstrap script has no Python runtime analogue")

    raise AssertionError(f"unclassified frozen MATLAB source: {path}")


def classify_manifest(manifest: Path) -> list[SourceClassification]:
    lines = [line for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines or lines[0].split("\t", 1)[0] != "path":
        raise AssertionError("unexpected MATLAB manifest header")

    records = [classify_source(line.split("\t", 1)[0]) for line in lines[1:]]
    if len(records) != EXPECTED_MATLAB_FILES:
        raise AssertionError(
            f"frozen source classification count {len(records)} != expected {EXPECTED_MATLAB_FILES}"
        )

    invalid = [record for record in records if record.status not in ALLOWED_STATUSES]
    if invalid:
        raise AssertionError(f"invalid v1 source classifications: {invalid[:10]}")
    if any(not record.evidence.strip() for record in records):
        raise AssertionError("every frozen source classification requires evidence")
    return records


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    records = classify_manifest(root / "reference" / "matlab_manifest.tsv")
    counts = {status: 0 for status in sorted(ALLOWED_STATUSES)}
    for record in records:
        counts[record.status] += 1
    rendered = " ".join(f"{status}={count}" for status, count in counts.items())
    print(f"V1 frozen source classification: PASS total={len(records)} {rendered}")


if __name__ == "__main__":
    main()
