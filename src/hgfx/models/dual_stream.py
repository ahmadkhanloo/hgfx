"""Two independent AR(1) binary HGF streams combined only at observation time."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import numpy as np

from .hgf_ar1_binary import ehgf_ar1_binary, hgf_ar1_binary, uhgf_ar1_binary

UpdateType = Literal["hgf", "ehgf", "uhgf"]

_FORWARD = {
    "hgf": hgf_ar1_binary,
    "ehgf": ehgf_ar1_binary,
    "uhgf": uhgf_ar1_binary,
}


def dual_ar1_binary(
    inputs,
    reward_parameters,
    social_parameters,
    *,
    update_type: UpdateType = "hgf",
    transformed: bool = False,
    irregular_intervals: bool | None = False,
    ignored_trials: Sequence[int] | None = None,
    validate: bool = True,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Run two stock AR1 binary HGFs on u[:,0] and u[:,1]."""

    if update_type not in _FORWARD:
        raise ValueError("update_type must be 'hgf', 'ehgf', or 'uhgf'")
    u = np.asarray(inputs, dtype=np.float64)
    if u.ndim != 2 or u.shape[1] < 2:
        raise ValueError("dual_ar1_binary expects u with at least two columns")
    forward = _FORWARD[update_type]
    kwargs = {
        "transformed": transformed,
        "irregular_intervals": irregular_intervals,
        "ignored_trials": ignored_trials,
        "validate": validate,
    }
    traj_r, inf_r = forward(u[:, 0], reward_parameters, **kwargs)
    traj_a, inf_a = forward(u[:, 1], social_parameters, **kwargs)
    levels = inf_r.shape[1]
    if inf_a.shape[1] != levels:
        raise ValueError("reward and social streams must have the same level count")
    traj = {f"{key}_r": value for key, value in traj_r.items()}
    traj.update({f"{key}_a": value for key, value in traj_a.items()})
    # MATLAB social-gaze layout: (:,1,1)=muhat_r, (:,1,3)=muhat_a, (:,3,*)=level-3.
    inf = np.full((u.shape[0], levels, 4), np.nan, dtype=np.float64)
    inf[:, :, 0] = inf_r[:, :, 0]
    inf[:, :, 1] = inf_r[:, :, 2]
    inf[:, :, 2] = inf_a[:, :, 0]
    inf[:, :, 3] = inf_a[:, :, 2]
    return traj, inf
