from sim_progress.Preload import SkillNode
from .utils.filters import _skill_node_filter
from .character import Character


class Yixuan(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sheer_attack_conversion_rate = {0: 0.3, 1: 0.1, 2: 0, 3: 0}      # 贯穿力转化字典{属性值（攻击力0，生命值1，防御力2，精通3）: 倍率}
        self.adrenaline_limit = 120     # 闪能最大值
        self.adrenaline = self.adrenaline_limit   # 入场时，获得满闪能

    def special_resources(self, *args, **kwargs) -> None:
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)

    def update_single_node_sp(self, node):
        """处理单个skill_node的回能——仪玄特化版，更新的自身的闪能"""
        if node.char_name == self.NAME:
            adrenaline_consume = node.skill.adrenaline_consume
            adrenaline_threshold = node.skill.adrenaline_threshold
            adrenaline_recovery = node.skill.adrenaline_recovery
            if self.sp < adrenaline_threshold:
                print(
                    f"{node.skill_tag}需要{adrenaline_threshold:.2f}点闪能，目前{self.NAME}仅有{self.adrenaline:.2f}点，需求无法满足，请检查技能树"
                )
            adrenaline_change = adrenaline_recovery - adrenaline_consume
            self.update_adrenaline(adrenaline_change)
        # Decibel
        self.process_single_node_decibel(node)

    def update_adrenaline(self, sp_value: int | float):
        """可全局强制更新能量的方法——仪玄特化版"""
        self.adrenaline += sp_value
        self.adrenaline = max(0.0, min(self.adrenaline, self.adrenaline_limit))

    def update_single_node_sp_overtime(self, args, kwargs):
        """处理单个skill_node的自然回能——仪玄特化版"""
        sp_regen_data = _sp_update_data_filter(*args, **kwargs)
        for mul in sp_regen_data:
            if mul.char_name == self.NAME:
                sp_change_2 = mul.get_sp_regen() / 60  # 每秒回能转化为每帧回能
                self.update_sp(sp_change_2)

    def get_resources(self) -> tuple[str, float]:
        pass

    def get_special_stats(self, *args, **kwargs) -> dict[str, int | float | bool]:
        """获取简仪玄特殊状态"""
        pass
