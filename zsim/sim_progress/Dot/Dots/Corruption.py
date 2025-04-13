from sim_progress.Dot import Dot
from dataclasses import dataclass
import sys


class Corruption(Dot):
    def __init__(self, bar=None):
        super().__init__(bar)  # 调用父类Dot的初始化方法
        self.ft = self.DotFeature()

    @dataclass
    class DotFeature(Dot.DotFeature):
        main_module = sys.modules['simulator.main_loop']
        char_name_box = main_module.init_data.name_box
        update_cd: int = 30
        index: str = 'Corruption'
        name: str = '侵蚀'
        dot_from: str = 'enemy'
        effect_rules: int = 2
        max_count: int = 1
        incremental_step: int = 1
        max_duration: int = 600
        """
        如果某角色在角色列表里，灼烧和最大生效次数就要发生变化。
        """
        if '某角色' in char_name_box:
            max_duration: int = 600 + 180
        max_effect_times = 30
