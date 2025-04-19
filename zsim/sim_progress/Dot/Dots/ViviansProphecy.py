from dataclasses import dataclass

from sim_progress.Buff import JudgeTools
from sim_progress.Dot import Dot
from sim_progress.Preload.SkillsQueue import spawn_node


class ViviansProphecy(Dot):
    def __init__(self):
        super().__init__()  # 调用父类Dot的初始化方法
        self.ft = self.DotFeature()
        preload_data = JudgeTools.find_preload_data()
        tick = JudgeTools.find_tick()
        self.skill_node_data = spawn_node(
            "1331_Core_Passive", tick, preload_data.skills
        )

    @dataclass
    class DotFeature(Dot.DotFeature):
        update_cd: int = 33
        index: str = "ViviansProphecy"
        name: str = "薇薇安的预言"
        dot_from: str = "薇薇安"
        effect_rules: int = 1
        max_count: int = 999999
        incremental_step: int = 1
        max_duration: int = 999999
        complex_exit_logic = True

    def exit_judge(self, **kwargs) -> bool:
        """薇薇安的预言 dot的退出逻辑：敌人只要处于异常状态，就不会退出。"""
        enemy = kwargs.get("enemy", None)
        if enemy is None:
            return False
        from sim_progress.Enemy import Enemy

        if not isinstance(enemy, Enemy):
            raise TypeError("enemy参数必须是Enemy类的实例")
        if not enemy.dynamic.is_under_anomaly():
            return True
        return False
