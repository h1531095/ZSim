from .BaseListenerClass import BaseListener


class ZanshinHerbCaseListener(BaseListener):
    """这个监听器的作用是记录残心青囊的触发信号"""

    def __init__(self, listener_id: str = None):
        super().__init__(listener_id)
        self.active_signal: tuple[object, bool] | None = None

    def listening_event(self, event_obj=None, **kwargs):
        """监听到失衡事件或是触发了新的异常事件时，记录这个信号。"""
        if "stun_event" in kwargs or "anomaly_event" in kwargs:
            self.active_signal = (event_obj, True)

    def listener_active(self):
        """置空信号"""
        self.active_signal = None
