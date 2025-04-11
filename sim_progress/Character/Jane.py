from sim_progress.Preload import SkillNode
from .filters import _skill_node_filter
from .character import Character

class Jane(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.passion: float = 0.0  # 狂热，0.0 ~ 100.0
        self.passion_stream: bool = False  # 狂热心流状态

    def special_resources(self, *args, **kwargs) -> None:
        """模拟简的狂特心流"""
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)