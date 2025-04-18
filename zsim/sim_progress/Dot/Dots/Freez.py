from sim_progress.Dot import Dot
import numpy as np
from dataclasses import dataclass
import sys


class Freez(Dot):
    def __init__(self, bar=None):
        super().__init__(bar)  # 调用父类Dot的初始化方法
        self.ft = self.DotFeature()

    @dataclass
    class DotFeature(Dot.DotFeature):
        main_module = sys.modules["simulator.main_loop"]
        enemy = main_module.schedule_data.enemy
        update_cd: int | float = np.inf
        index: str = "Freez"
        name: str = "冻结"
        dot_from: str = "enemy"
        effect_rules: int = 4
        max_count: int = 1
        incremental_step: int = 1
        max_duration: int = 240 * (1 + enemy.freeze_resistance)
        max_effect_times = 1

    def start(self, timenow):
        self.dy.active = True
        self.dy.start_ticks = timenow
        self.dy.last_effect_ticks = timenow
        self.dy.end_ticks = self.dy.start_ticks + self.ft.max_duration
        self.history.start_times += 1
        self.history.last_start_ticks = timenow
        self.dy.count = 1
        self.dy.effect_times = 1
        self.dy.ready = True
