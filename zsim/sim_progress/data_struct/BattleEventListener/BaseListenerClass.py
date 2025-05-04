from abc import ABC, abstractmethod


class BaseListener(ABC):
    @abstractmethod
    def __init__(self, listener_id: str = None):
        self.listener_id: str | None = listener_id
        self.schedule = None

    @abstractmethod
    def listening_event(self, event, **kwargs):
        """监听事件的函数"""
        pass

    @abstractmethod
    def listener_active(self):
        """当监听到预期事件时，监听器的激活函数"""
        pass

