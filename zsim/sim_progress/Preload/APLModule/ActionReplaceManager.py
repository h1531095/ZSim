from abc import ABC, abstractmethod


class ActionReplaceManager:
    """
    该对象主要用于阻塞、改写APL运行结果。
    由于是非常粗暴的接在APL的对外输出函数上进行拦截、修正，
    所以该对象的使用必须谨慎，以免大幅度影响APL手法的实现。
    """

    def __init__(self, preload_data):
        self.preload_data = preload_data
        self.quick_assist_strategy = self.QuickAssistStrategy(self.preload_data)

    def action_replace_factory(
        self, CID: int, action: str, tick: int
    ) -> tuple[bool, str]:
        """该函数主要用于拦截APL的主动动作，使其被其他动作替代，用来模拟各种特殊情况"""
        if self.quick_assist_strategy.condition_judge(
            CID=CID, action=action, tick=tick
        ):
            action = self.quick_assist_strategy.spawn_new_action(CID, action)
            return True, action
        return False, action

    class __BaseStrategy(ABC):
        def __init__(self, preload_data):
            self.preload_data = preload_data

        @abstractmethod
        def condition_judge(self, *args, **kwargs):
            pass

        @abstractmethod
        def spawn_new_action(self, *args, **kwargs):
            pass

    class QuickAssistStrategy(__BaseStrategy):
        def __init__(self, preload_data):
            super().__init__(preload_data)
            self.manager_box = {}

        def condition_judge(self, *args, **kwargs) -> bool:
            """
            该函数用于判定当前tick的动作是否需要被替换成快速支援：条件如下：
            1、当前角色快速支援亮起
            2、当前角色企图从后台切到前台
            """
            CID = kwargs.get("CID", None)
            tick = kwargs.get("tick", None)
            action = kwargs.get("action", None)
            if CID is None or action is None:
                raise ValueError("CID或action为空！")
            if self.preload_data.quick_assist_system is None:
                """如果快速支援系统的对象还未建立，那么说明此时
                根本不可能有导致快速支援替换APL动作的情况发生，直接返回False即可。"""
                return False
            if CID not in self.manager_box:
                for manager in self.preload_data.quick_assist_system.quick_assist_manager_group.values():
                    if manager.char.CID == CID:
                        self.manager_box[CID] = manager
                        break
                else:
                    raise ValueError(f"没有找到{CID}角色的快速支援管理器！")
            current_manager = self.manager_box[CID]
            node_on_field = self.preload_data.get_on_field_node(tick - 1)
            """注意，这里传入tick-1的作用：当某些技能不能被合轴与终止时（比如QTE和Q），新动作会被SwapCancelEngine一直拦截，
            此时，就会出现1帧时间场上没有任何动作，这会导致调用该函数的一些判断出错。所以将时间提前了1帧，规避这些错误。"""
            if node_on_field is None:
                # FIXME:这里还是有问题，程序中有时会出现的current_node_on_field 为None的情况一定会干扰模拟的进行，必须找时间解决掉！
                return False
            """当前角色的快速支援正处于激活状态，并且角色企图上场释放技能，则执行替换。"""
            if (
                current_manager.quick_assist_available
                and str(CID) not in node_on_field.skill_tag
            ):
                return True
            else:
                return False

        def spawn_new_action(self, CID: int, action: str):
            CID = int(action.split("_")[0].strip())
            for _obj in self.preload_data.skills:
                if _obj.CID != CID:
                    continue
                do_immediately_info = _obj.get_skill_info(skill_tag=action, attr_info="do_immediately")
                if do_immediately_info:
                    return action
                else:
                    manager = self.manager_box[CID]
                    # print(f'执行快速支援！技能{action}替换成了{manager.quick_assist_skill}！')
                    return manager.quick_assist_skill
            else:
                raise ValueError(f"没有找到CID为{CID}的技能对象！无法执行快速支援替换！")
