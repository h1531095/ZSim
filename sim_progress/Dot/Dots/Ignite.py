from sim_progress.Dot import Dot
from dataclasses import dataclass
import sys


class Ignite(Dot):
    """
    灼烧dot，固定时间，内置CD0.5s
    """
    def __init__(self, bar=None):
        super().__init__(bar)  # 调用父类Dot的初始化方法
        self.ft = self.DotFeature()  # 用Ignite的DotFeature替代默认的DotFeature

    # 你可以在这里添加特定于Ignite的行为或方法
    @dataclass
    class DotFeature(Dot.DotFeature):
        main_module = sys.modules['simulator.main_loop']
        char_name_box = main_module.global_stats.name_box
        update_cd: int = 30
        index: str = 'Ignite'
        name: str = '灼烧'
        dot_from: str = 'enemy'
        effect_rules: int = 1
        max_count: int = 1
        incremental_step: int = 1
        """
        如果柏妮思在角色列表里，灼烧和最大生效次数就要发生变化。
        """
        if '柏妮思' in char_name_box:
            max_duration: int = 600 + 180
        else:
            max_duration = 600
        max_effect_times = 30
    




        



