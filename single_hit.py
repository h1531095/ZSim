from dataclasses import dataclass
import numpy as np


@dataclass
class SingleHit:
    """Feedback to enemy for a single hit."""
    skill_tag: str
    snapshot: tuple[int, np.float64, np.ndarray]
    stun: np.float64
    dmg_expect: np.float64
    dmg_crit: np.float64