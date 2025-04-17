from sim_progress.Preload import SkillNode
from ..utils.filters import _skill_node_filter
from ..character import Character


class Vivian(Character):
    """薇薇安的特殊资源模块"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.feather_manager = None     # 羽毛管理器（飞羽、护羽的获取、切换）


    def special_resources(self, *args, **kwargs) -> None:
        # 输入类型检查
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            pass

    def get_resources(self) -> tuple[str, float]:
        pass

    def get_special_stats(self, *args, **kwargs) -> dict[str, int | float | bool]:
        pass
