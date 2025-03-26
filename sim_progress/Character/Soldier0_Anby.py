from sim_progress.Preload import SkillNode
from .filters import _skill_node_filter
from .character import Character
import sys


class Soldier0_Anby(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.silver_star: float = 0.0   # 银星
        self.max_silver_star: float = 100.0     # 银星上限
        self.silver_star_gain_ratio: float = 1.0        # 银星获得效率
        self.silver_star_gain_dict: dict[str: float] = {
            '1381_NA_1': 4.6875,
            '1381_NA_2': 7.53472222,
            '1381_NA_3_A': 15.12152778,
            '1381_NA_4': 2.34375,
            '1381_NA_5': 18.75,
            '1381_E_A': 11.11,
            '1381_E_EX': 100.1,
            '1381_CA': 50.1,
            '1381_QTE': 40.625,
            '1381_Q': 100.1,
            '1381_BH_Aid': 6.25,
            '1381_Assault_Aid': 6.25
        }
