from sim_progress.Character.utils.filters import _skill_node_filter, _sp_update_data_filter
from sim_progress.Character import Character
from typing import TYPE_CHECKING

from simulator.simulator_class import Simulator

if TYPE_CHECKING:
    from sim_progress.Preload import SkillNode
from .AdrenalineManagerClass import AdrenalineManager


class Yixuan(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sheer_attack_conversion_rate = {0: 0.3, 1: 0.1, 2: 0, 3: 0}      # 贯穿力转化字典{属性值（攻击力0，生命值1，防御力2，精通3）: 倍率}
        self.adrenaline_limit = 120     # 闪能最大值
        self.adrenaline = self.adrenaline_limit   # 入场时，获得满闪能
        self.technique_points: float = 0.0      # 术法值
        self.adrenaline_manager = AdrenalineManager()
        self.listener_build = False
        self.__adrenaline_recover_overtime_update_tick = 0          # 上次更新闪能自然恢复的时间

    def special_resources(self, *args, **kwargs) -> None:
        # 输入类型检查
        if not self.listener_build:
            if not isinstance(self.sim_instance, Simulator):
                raise TypeError("仪玄对象中的sim_instance不是Simulator类")
            self.sim_instance.listener_manager.listener_factory(initiate_signal="Yixuan_1",  sim_instance=self.sim_instance)
            self.listener_build = True
        skill_nodes: list["SkillNode"] = _skill_node_filter(*args, **kwargs)
        for __nodes in skill_nodes:
            # TODO: 把每个技能广播给adrenaline manager，更新闪能恢复事件。
            if __nodes.char_name != self.NAME:
                continue

    def update_sp(self, sp_value: float):
        """仪玄没有能量值，所以这里update_sp直接return置空"""
        return

    def update_adrenaline(self, sp_value: int | float):
        """可全局强制更新能量的方法——仪玄特化版"""
        self.adrenaline += sp_value
        self.adrenaline = max(0.0, min(self.adrenaline, self.adrenaline_limit))

    def __update_adrenaline(self, skill_node: "SkillNode"):
        """char对象内部更新闪能的方法"""
        if skill_node.char_name != self.NAME:
            raise ValueError(f"{self.NAME}的更新闪能的方法接收到了非仪玄的SkillNode")
        adrenaline_delta = skill_node.skill.adrenaline_recovery - skill_node.skill.adrenaline_consume
        if adrenaline_delta <= 0 and abs(adrenaline_delta) > self.adrenaline:
            raise ValueError(f"检测到技能{skill_node.skill_tag}（{skill_node.skill.skill_text}）企图消耗{skill_node.skill.adrenaline_consume}点闪能，但是仪玄当前的闪能不足：{self.adrenaline}，请检查APL")
        self.update_adrenaline(adrenaline_delta)

    def update_single_node_sp_overtime(self, args, kwargs):
        """
        该函数会在Preload以及Schedule阶段被调用两次，当在Preload阶段调用时，sp_regen_data为空，
        只有在Schedule阶段被调用时，函数才会被执行。
        所以sp_regen_data虽然和闪能回复无关，但确是保证函数只被运行一次的关键。
        """
        sp_regen_data = _sp_update_data_filter(*args, **kwargs)
        if sp_regen_data:
            if self.sim_instance.tick == self.__adrenaline_recover_overtime_update_tick and self.__adrenaline_recover_overtime_update_tick != 0:
                raise ValueError("检测到仪玄闪能的自然恢复逻辑在同一个tick被调用了两次！请检查函数！")
            sp_change_per_tick = 2 / 60
            self.update_adrenaline(sp_change_per_tick)
            self.__adrenaline_recover_overtime_update_tick = self.sim_instance.tick

    def get_resources(self) -> tuple[str, float]:
        pass

    def get_special_stats(self, *args, **kwargs) -> dict[str, int | float | bool]:
        """获取简仪玄特殊状态"""
        pass

