from .BaseListenerClass import BaseListener


class HeartstringNocturneListener(BaseListener):
    """监听入场事件，并且直接添加心弦夜响Buff"""

    def __init__(self, listener_id: str = None):
        super().__init__(listener_id)
        self.active_signal = None

    def listening_event(self, event, **kwargs):
        """监听到角色入场事件，传递入场信号。"""
        if "enter_battle_event" not in kwargs:
            return
        from sim_progress.Preload import SkillNode

        if not isinstance(event, SkillNode):
            raise ValueError("entr_battle_event的事件对象必须是SkillNode类型！")
        self.active_signal = (event, True)

    def listener_active(self):
        self.active_signal = None
