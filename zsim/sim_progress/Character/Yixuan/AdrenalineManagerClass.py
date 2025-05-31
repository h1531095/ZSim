from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sim_progress.Character import Character
    from Preload import SkillNode
from .AdrenalineEventClass import BaseAdrenalineEvent


class AdrenalineManager:
    """仪玄有各种回复闪能的事件，所以统一写一个Manger来管理它们。"""
    def __init__(self, char_instance: "Character"):
        self.char = char_instance
        self.adrenaline_recover_event_group: list[BaseAdrenalineEvent] = []

    def broadcast(self, skill_node: "SkillNode"):
        """向所有回能事件进行广播"""
        for event in self.adrenaline_recover_event_group:
            event.update_status(skill_node=skill_node)


