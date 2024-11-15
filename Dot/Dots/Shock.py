from Dot import Dot
from dataclasses import dataclass
import sys


class Shock(Dot):
    def __init__(self, bar=None):
        super().__init__(bar)  # 调用父类Dot的初始化方法
        self.ft = self.DotFeature()

    @dataclass
    class DotFeature(Dot.DotFeature):
        main_module = sys.modules['__main__']
        char_name_box = main_module.init_data.name_box
        update_cd: int = 60
        index: str = 'Shock'
        name: str = '感电'
        dot_from: str = 'enemy'
        effect_rules: int = 2
        max_count: int = 1
        incremental_step: int = 1
        """
        如果丽娜在角色列表里，灼烧和最大生效次数就要发生变化。
        """
        if '丽娜' in char_name_box:
            max_duration: int = 600 + 180
        else:
            max_duration: int = 600
        max_effect_times = 30
