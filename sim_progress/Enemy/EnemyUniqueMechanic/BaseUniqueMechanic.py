from abc import ABC, abstractmethod


class BaseUniqueMechanic:
    def __init__(self, enemy_instance):
        self.enemy = enemy_instance
        self.special_event_manager = None


class BaseSpecialEvent(ABC):
    def __init__(self, enemy_instance):
        self.enemy = enemy_instance
        self.introduction = None

    @ abstractmethod
    def event_happend(self):
        pass


