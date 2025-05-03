from sim_progress.Preload import SkillNode
from .utils.filters import _skill_node_filter
from .character import Character


class Hugo(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def special_resources(self, *args, **kwargs) -> None:
        """雨果的特殊资源模块"""
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            pass

    def get_resources(self) -> tuple[str, float]:
        pass

    def get_special_stats(self, *args, **kwargs) -> dict[str, int | float | bool]:
        pass