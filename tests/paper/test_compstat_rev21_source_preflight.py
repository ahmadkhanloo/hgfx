"""Synthetic-only REV-2.1 source/transform preflight contracts.

No real MATLAB/HGFX model is called and no participant data is loaded.
"""
from __future__ import annotations

import math
from pathlib import Path
import tempfile
import unittest

from tools.compstat_rev21_source_preflight import (
    BASELINE_BLOB,
    DEFAULT_NATIVE_BASELINE,
    PHI2_ZERO_BASED,
    SELECTION_SEED,
    SELECTION_SHA256,
    fixed_block_selection,
    git_blob_id,
    inspect_phi2_domain,
    original_statuses,
    parse_original_native_vector,
)

ORIGINAL_LITERAL=(
    "import numpy as np\n"
    "P = np.asarray([np.nan,0,1,np.nan,.1,1,np.nan,0,.2,"
    "np.nan,0,1,1,1,np.nan,-2,-6],dtype=np.float64)\n"
)
HGF_PRIOR_SOURCE="""switch update_type
    case 'hgf'
        c.logitphisa = [NaN, 1, 1];
    case {'ehgf', 'uhgf'}
        c.logitphisa = [NaN, 0, 0];
"""
MATLAB_TRANSFORM_SOURCE=(
    "pvec(2*l+1:3*l) = tapas_sgm(ptrans(2*l+1:3*l),1);"
)


class Rev21SourcePreflight(unittest.TestCase):
    def test_parse_original_native_vector_literal_exact(self):
        native=parse_original_native_vector(ORIGINAL_LITERAL)
        self.assertEqual(len(native),17)
        self.assertTrue(all((math.isnan(a) and math.isnan(b)) or a==b
                            for a,b in zip(native,DEFAULT_NATIVE_BASELINE)))
        self.assertEqual(native[PHI2_ZERO_BASED],0.0)
        self.assertEqual(native[8],0.2)

    def test_reject_nonliteral_or_duplicate_native_vectors(self):
        with self.assertRaises(ValueError):
            parse_original_native_vector("P = np.asarray([1, helper()])")
        with self.assertRaises(ValueError):
            parse_original_native_vector(ORIGINAL_LITERAL+ORIGINAL_LITERAL)

    def test_hgf_prior_phi2_positive_variance_and_no_finite_logit_origin(self):
        native=parse_original_native_vector(ORIGINAL_LITERAL)
        result=inspect_phi2_domain(native,HGF_PRIOR_SOURCE,MATLAB_TRANSFORM_SOURCE)
        self.assertEqual(result["native_vector_index_zero_based"],7)
        self.assertTrue(result["is_free_under_original_hgf_prior"])
        self.assertEqual(result["transformed_prior_variance"],1.0)
        self.assertFalse(result["finite_inverse_logit_exists"])
        self.assertIsNone(result["inverse_logit_when_finite"])

    def test_native_boundary_one_is_also_undefined_without_clipping(self):
        p=list(DEFAULT_NATIVE_BASELINE)
        p[PHI2_ZERO_BASED]=1.0
        d=inspect_phi2_domain(tuple(p),HGF_PRIOR_SOURCE,MATLAB_TRANSFORM_SOURCE)
        self.assertFalse(d["finite_inverse_logit_exists"])
        self.assertIsNone(d["inverse_logit_when_finite"])

    def test_native_interior_is_transformable_and_not_silently_modified(self):
        p=list(DEFAULT_NATIVE_BASELINE)
        p[PHI2_ZERO_BASED]=0.4
        d=inspect_phi2_domain(tuple(p),HGF_PRIOR_SOURCE,MATLAB_TRANSFORM_SOURCE)
        self.assertTrue(d["finite_inverse_logit_exists"])
        self.assertAlmostEqual(d["inverse_logit_when_finite"],math.log(2/3))
        self.assertEqual(p[PHI2_ZERO_BASED],0.4)

    def test_wrong_hgf_prior_or_transformation_is_rejected(self):
        native=parse_original_native_vector(ORIGINAL_LITERAL)
        with self.assertRaisesRegex(ValueError,"prior variance"):
            inspect_phi2_domain(native,HGF_PRIOR_SOURCE.replace(
                "c.logitphisa = [NaN, 1, 1]",
                "c.logitphisa = [NaN, 0, 0]"),MATLAB_TRANSFORM_SOURCE)
        with self.assertRaisesRegex(ValueError,"transform"):
            inspect_phi2_domain(native,HGF_PRIOR_SOURCE,
                                "pvec = ptrans;")

    def test_all_64_reed_and_fixed_independent_suthaharan_subset(self):
        s=fixed_block_selection()
        self.assertEqual(s["seed"],2026111021)
        self.assertEqual(s["selected_suthaharan_blocks"],64)
        self.assertEqual(s["all_original_reed_blocks"],64)
        self.assertEqual(s["total_multivector_source_blocks"],128)
        self.assertEqual(s["selected_suthaharan_case_ids_sha256"],
                         SELECTION_SHA256)
        self.assertEqual(SELECTION_SHA256,
                         "adcb0e8694e72c8c82e4ae3416d54d409273729dea0558b9c3e31043d5c06047")
        self.assertFalse(s["raw_case_ids_exported"])

    def test_corrupted_historical_zip_rejected_before_observation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"unverified.zip"
            p.write_bytes(b"an example, not an original scientific archive")
            with self.assertRaisesRegex(ValueError,"ZIP SHA"):
                original_statuses(p)

    def test_git_blob_sha_uses_binary_git_header(self):
        self.assertEqual(git_blob_id(b"test\n"),
                         "9daeafb9864cf43055ae93beb0afd6c7d144bfa4")


if __name__=="__main__":
    unittest.main()
