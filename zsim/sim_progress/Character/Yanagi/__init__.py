from .StanceManager import StanceManager
from sim_progress.Preload import SkillNode
from sim_progress.Character.utils.filters import _skill_node_filter
from sim_progress.Character import Character


class Yanagi(Character):
    """柳的特殊资源系统"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stance_manager = StanceManager(self)

    def special_resources(self, *args, **kwargs) -> None:
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        # tick = kwargs.get('tick', 0)
        for nodes in skill_nodes:
            self.stance_manager.update_myself(nodes)

    def get_resources(self) -> tuple[str|None, int|float|bool|None]:
        """柳的get_resource不返回内容！因为柳没有特殊资源，只有特殊状态"""
        return None, None

    def get_special_stats(self, *args, **kwargs) -> dict[str|None, object|None]:
        return {'当前架势': self.stance_manager.stance_now,
                '森罗万象状态': self.stance_manager.shinrabanshou.active()}
