from sim_progress import Character
from .StanceManager import StanceManager


class Yanggi(Character):
    """柳的特殊资源系统"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stance_manager = StanceManager(self)

    def special_resources(self, *args, **kwargs) -> None:
        pass

    def get_resources(self) -> tuple[str|None, int|float|bool|None]:
        """柳的get_resource不返回内容！因为柳没有特殊资源，只有特殊状态"""
        return None, None


    def get_special_stats(self, *args, **kwargs) -> dict[str|None, object|None]:

        return {'当前架势': self.stance_manager.stance_now, '森罗万象状态': self.stance_manager.shinrabanshou}
