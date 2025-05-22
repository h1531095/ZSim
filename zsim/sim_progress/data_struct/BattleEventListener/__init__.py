from .BaseListenerClass import BaseListener
import importlib
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simulator.simulator_class import Simulator


class ListenerManger:
    """监听器组"""

    def __init__(self, sim_instance: "Simulator"):
        self.sim_instance = sim_instance
        self._listeners_group: dict[str, BaseListener] = {}
        self.__listener_map: dict[str, str] = {
            "Hugo_1": "HugoCorePassiveBuffListener",
            "Hormone_Punk_1": "HormonePunkListener",
            "Zenshin_Herb_Case_1": "ZanshinHerbCaseListener",
            "Heartstring_Nocturne_1": "HeartstringNocturneListener",
        }

    def add_listener(self, listener: BaseListener):
        """添加一个监听器"""
        self._listeners_group[listener.listener_id] = listener

    def remove_listener(self, listener: BaseListener):
        """移除一个监听器"""
        self._listeners_group.pop(listener.listener_id)

    def broadcast_event(self, event, **kwargs):
        """广播事件，kwargs参数中记录了事件类型"""
        for listener in self._listeners_group.values():
            listener.listening_event(event, **kwargs)

    def listener_factory(self, initiate_signal: str = None, sim_instance: "Simulator" = None):
        """初始化监听器的工厂函数"""
        if initiate_signal is None:
            raise ValueError(
                "在初始化阶段调用监听器工厂函数时，必须传入有效的initiate_signal参数！"
            )
        for listener_id, listener_class_name in self.__listener_map.items():
            if initiate_signal in listener_id:
                module_name = listener_class_name
                try:
                    module = importlib.import_module(
                        f".{module_name}", package=__name__
                    )
                    listener_obj = getattr(module, listener_class_name)(listener_id, sim_instance=sim_instance)
                    self.add_listener(listener_obj)
                    return listener_obj
                except ModuleNotFoundError:
                    raise ValueError(
                        "在初始化阶段调用监听器工厂函数时，找不到对应的监听器模块！"
                    )

#
# # import时，就创建一个单例
# listener_manager_instance = ListenerManger()
