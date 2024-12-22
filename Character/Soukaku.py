from Preload import SkillNode
from Report import report_to_log
from .filters import _skill_node_filter
from .character import Character
from Buff.BuffAddStrategy import BuffAddStrategy

class Soukaku(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vortex: int = 0  # 涡流初始0点

    def special_resources(self, *args, **kwargs) -> None:
        """模拟苍角的涡流机制"""
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        # 对输入的skill_node进行遍历
        for node in skill_nodes:
            if '1131' not in node.skill_tag:
                continue
            if self.vortex <= 3:
                if node.skill_tag in ['1131_E_EX_1', '1131_E_EX_2', '1131_E_EX_3', '1131_QTE']:
                    self.vortex += 1
                    report_to_log(f"[Character] 苍角的涡流被更新为 {self.vortex}")
                elif node.skill_tag == '1131_Q':
                    self.vortex = 3
                    report_to_log(f"[Character] 苍角的涡流被更新为 {self.vortex}")
            # 这里不能 elif
            if self.vortex >= 3:
                if node.skill_tag in ['1131_E_EX_A', '1131_QTE', '1131_Q']:
                    self.vortex = 0
                    BuffAddStrategy('Buff-角色-苍角-核心被动-2')
                    report_to_log(f"[Character] 苍角的涡流被更新为 {self.vortex}")

    def get_resources(self, *args, **kwargs) -> tuple[str | None, int | float | None]:
        return '涡流', self.vortex