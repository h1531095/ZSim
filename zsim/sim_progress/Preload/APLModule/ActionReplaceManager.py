from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sim_progress.Preload.PreloadDataClass import PreloadData
    from sim_progress.Character.character import Character
    from sim_progress.data_struct import EnemyAttackEventManager


class ActionReplaceManager:
    """
    该对象主要用于阻塞、改写APL运行结果。
    由于是非常粗暴的接在APL的对外输出函数上进行拦截、修正，
    所以该对象的使用必须谨慎，以免大幅度影响APL手法的实现。
    """

    def __init__(self, preload_data):
        self.preload_data: "PreloadData" = preload_data
        self.quick_assist_strategy = self.QuickAssistStrategy(self.preload_data)
        self.parry_aid_strategy = self.ParryAidStrategy(self.preload_data)

    def action_replace_factory(
        self, CID: int, action: str, tick: int
    ) -> tuple[bool, str]:
        """该函数主要用于拦截APL的主动动作，使其被其他动作替代，用来模拟各种特殊情况"""
        """如果目前正处于黄光阶段（窗口期），那么此时的所有切人动作都会被无条件换成格挡"""
        atk_manager = self.preload_data.atk_manager
        if self.quick_assist_strategy.condition_judge(
            CID=CID, action=action, tick=tick
        ):
            action = self.quick_assist_strategy.spawn_new_action(CID, action)
            return True, action
        return False, action
        # if "耀嘉音" in self.preload_data.sim_instance.init_data.name_box:
        #     pass
        # else:
        #     # TODO: 连续格挡的动作替换逻辑
        #
        #     if self.quick_assist_strategy.condition_judge(
        #         CID=CID, action=action, tick=tick
        #     ):
        #         action = self.quick_assist_strategy.spawn_new_action(CID, action)
        #         return True, action
        #     return False, action

    class __BaseStrategy(ABC):
        def __init__(self, preload_data):
            self.preload_data: "PreloadData" = preload_data

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

        def condition_judge(
            self, CID: int, tick: int, action: str, *args, **kwargs
        ) -> bool:
            """
            该函数用于判定当前tick的动作是否需要被替换成快速支援：条件如下：
            1、当前角色快速支援亮起
            2、当前角色企图从后台切到前台
            """
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
                # FIXME:这里还是有问题，程序中有时会出现的current_node_on_field 为None的情况，一定会干扰模拟的进行，必须找时间解决掉！

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

                do_immediately_info = _obj.get_skill_info(
                    skill_tag=action, attr_info="do_immediately"
                )

                if do_immediately_info:
                    return action
                else:
                    manager = self.manager_box[CID]
                    # print(f'执行快速支援！技能{action}替换成了{manager.quick_assist_skill}！')
                    return manager.quick_assist_skill
            else:
                raise ValueError(
                    f"没有找到CID为{CID}的技能对象！无法执行快速支援替换！"
                )

    class ParryAidStrategy(__BaseStrategy):
        """负责将技能tag替换成各类招架支援的结构"""

        def __init__(self, preload_data):
            super().__init__(preload_data)
            self.consecutive_parry_mode: bool = False  # 连续招架模式
            self.parry_interaction_in_progress: bool = False  # 当前轮次招架交互正在进行
            self.parry_tag: str | None = None  # 当前轮次招架交互的招架技能标签。

        def condition_judge(
            self, CID: int, tick: int, action: str, *args, **kwargs
        ) -> bool:
            """
            用来判断当前tick的动作是否要被换成招架（前置条件判断），核心条件有：
            1、有角色试图从后台切到前台
            2、该角色是近战角色，具有招架支援能力
            3、敌方正处于进攻状态，并且存在有效交互窗口。
            """
            char_switch: bool
            char_on_field: int | None = self.preload_data.operating_now
            char_obj: "Character" = self.preload_data.char_data.find_char_obj(CID=CID)
            atk_manager: "EnemyAttackEventManager" = self.preload_data.atk_manager
            if char_on_field is None:
                """第一个动作，也会被视为从后台切入前台"""
                char_switch = True
            else:
                if char_on_field == CID:
                    char_switch = False
                else:
                    char_switch = True
            if not char_switch:
                return False
            if char_obj.aid_type != "招架":
                # TODO：暂时不支持回避支援。
                return False
            if atk_manager.attacking and atk_manager.action.parryable:
                """注意，这里不需要对细节进行判断，只要当前tick正处于进攻交互事件期间，该结构直接放行。"""
                return True
            return False

        def spawn_new_action(self, CID: int, action: str, *args, **kwargs):
            """根据当前的状态，执行招架支援tag的替换。"""
            atk_manager = self.preload_data.atk_manager
            if atk_manager.action.hit == 1:
                if self.parry_interaction_in_progress:
                    if not atk_manager.is_answered:
                        raise ValueError(
                            "技能tag替换管理器中，已经进入招架阶段，但是进攻事件管理器中的响应状态并未打开，二者状态不一致，请检查！"
                        )
                    """如果此时正处于招架状态，"""
                    return self.spawn_parry_aid_tag(CID, mode=3)
                else:
                    self.parry_interaction_in_progress = True
                    if atk_manager.action.hit_type == "Light":
                        return self.spawn_parry_aid_tag(CID, mode=0)
                    elif atk_manager.action.hit_type == "Heavy":
                        return self.spawn_parry_aid_tag(CID, mode=2)

            elif atk_manager.action.hit > 1 and not self.parry_interaction_in_progress:
                """连续招架的第一次招架"""
                return self.spawn_parry_aid_tag(CID, mode=1)

        @staticmethod
        def spawn_parry_aid_tag(CID: int, mode: int):
            if mode == 0:
                return f"{CID}_Light_parry_Aid"
            elif mode == 1:
                return f"{CID}_Chain_parry_Aid"
            elif mode == 2:
                return f"{CID}_Heavy_parry_Aid"
            elif mode == 3:
                """这是衔接在招架支援后的后退动作，无法取消。"""
                return f"{CID}_Chain_parry_Aid"
            else:
                raise ValueError(f"不支持的招架模式：{mode}！")
        

