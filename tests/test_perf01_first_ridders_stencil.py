"""Fail-closed synthetic controls for source-ordered Ridders ± stencil archives."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"benchmarks"/"runtime_v1"
sys.path.insert(0,str(SRC))
import subject7_first_ridders_stencil as r
import verify_first_ridders_matlab_raw as mat


def nodes(nsteps=(11,11,11)):
    res=[{"ordinal":0,"x":r.START.copy(),
          "x_hex":r.xhex(r.START),"value":100.}]
    for j in range(3):
        h=1.
        for k in range(nsteps[j]):
            for sign in (1,-1):
                v=r.START.copy()
                v[j]=r.START[j]+sign*h
                res.append({"ordinal":len(res),"x":v,"x_hex":r.xhex(v),
                            "value":float(100.0+j+sign*h)})
            h/=1.2
    return res


class OriginalStencilTests(unittest.TestCase):
    def test_positive_all_3_min_11_pairs(self):
        counts,rows=r.classify_stencil(nodes())
        self.assertEqual(counts,[11,11,11])
        self.assertEqual(len(rows),33)

    def test_unbalanced_but_valid_source_3_axes(self):
        counts,rows=r.classify_stencil(nodes((11,13,15)))
        self.assertEqual(counts,[11,13,15])
        self.assertEqual(len(rows),39)

    def test_exact_same_x_source_bit_difference_detected(self):
        a=r.START.copy()
        b=a.copy()
        b[0]=np.nextafter(b[0],-np.inf)
        self.assertNotEqual(r.xbits(a),r.xbits(b))

    def test_wrong_center_coordinate_is_rejected(self):
        z=nodes()
        z[0]["x"][0]+=0.5
        z[0]["x_hex"]=r.xhex(z[0]["x"])
        with self.assertRaisesRegex(ValueError,"center"):
            r.classify_stencil(z)

    def test_wrong_center_hex_is_rejected(self):
        z=nodes()
        z[0]["x_hex"][0]="0"*16
        with self.assertRaisesRegex(ValueError,"x bits"):
            r.classify_stencil(z)

    def test_dropped_positive_negative_pair_member_is_rejected(self):
        z=nodes()
        z.pop(2)
        for i,e in enumerate(z):e["ordinal"]=i
        with self.assertRaisesRegex(ValueError,"pair"):
            r.classify_stencil(z)

    def test_negative_positive_order_swap_fails(self):
        z=nodes()
        z[1],z[2]=z[2],z[1]
        z[1]["ordinal"]=1;z[2]["ordinal"]=2
        with self.assertRaisesRegex(ValueError,"sign/order"):
            r.classify_stencil(z)

    def test_axis_skip_is_rejected(self):
        z=nodes()
        for i,record in enumerate(z[1:23],start=1):
            x=record["x"]
            x[2]=x[0]
            x[0]=r.START[0]
            record["x_hex"]=r.xhex(x)
        with self.assertRaisesRegex(ValueError,"order"):
            r.classify_stencil(z)

    def test_insufficient_original_ten_minimum_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"min_steps"):
            r.classify_stencil(nodes((10,11,11)))

    def test_too_many_original_maximum_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"max_steps"):
            r.classify_stencil(nodes((11,101,11)))

    def test_disordered_source_ordinals_are_rejected(self):
        z=nodes();z[5]["ordinal"]=999
        with self.assertRaisesRegex(ValueError,"ordinal"):
            r.classify_stencil(z)

    def test_nonfinite_original_fails(self):
        z=nodes();z[8]["value"]=float("nan")
        with self.assertRaisesRegex(ValueError,"value"):
            r.classify_stencil(z)

    def test_frozen_source_model_status_source_is_not_dummy(self):
        self.assertEqual(r.HGFX,"4dd8fbd8239d05f2c7932a9a9b3b7795f0a9ab27")
        self.assertEqual(r.MATLAB,"2437f4dc241541072722a2695ddeca7b44d83dd3")
        self.assertNotEqual(r.BFGS_H,r.BFGS_M)

    def test_raw_mat_metadata_must_exist(self):
        with self.assertRaises((KeyError,ValueError,TypeError)):
            mat.inspect_mat(Path("/dev/null"),{},b"missing",{})


if __name__=="__main__": unittest.main()
