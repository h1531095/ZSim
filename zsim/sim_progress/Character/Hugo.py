# from sim_progress.Preload import SkillNode
# from .utils.filters import _skill_node_filter
from .character import Character
from sim_progress.data_struct import listener_manager_instance


class Hugo(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 虽然雨果自身没有特殊资源，但是需要创建他的专属监听器
        listener_manager_instance.listener_factory(initiate_signal="Hugo")

    def special_resources(self, *args, **kwargs) -> None:
        """雨果的特殊资源模块"""
        return

    def get_resources(self) -> tuple[str, float]:
        pass

    def get_special_stats(self, *args, **kwargs) -> dict[str, int | float | bool]:
        pass
