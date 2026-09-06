from dataclasses import dataclass
from typing import Any


@dataclass
class FitResult:
    p_prc: Any = None
    p_obs: Any = None
    traj: Any = None
    optim: Any = None
    yhat: Any = None
    res: Any = None
    irr: Any = None
