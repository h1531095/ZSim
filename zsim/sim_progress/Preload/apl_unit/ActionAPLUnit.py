from typing import TYPE_CHECKING
from sim_progress.Preload.apl_unit.APLUnit import APLUnit

if TYPE_CHECKING:
    from simulator.simulator_class import Simulator
    from sim_progress.Preload import PreloadData


class ActionAPLUnit(APLUnit):
    def __init__(self, apl_unit_dict: dict):
        """动作类APL，目前也只有这一种APL类型。"""
        super().__init__()
        self.char_CID = apl_unit_dict["CID"]
        self.priority = apl_unit_dict["priority"]
        self.apl_unit_type = apl_unit_dict["type"]
        self.break_when_found_action = True
        self.result = apl_unit_dict["action"]
        from sim_progress.Preload.apl_unit.APLUnit import spawn_sub_condition

        for condition_str in apl_unit_dict["conditions"]:
            self.sub_conditions_unit_list.append(
                spawn_sub_condition(self.priority, condition_str)
            )

    def check_all_sub_units(
        self, found_char_dict, game_state, sim_instance: "Simulator", **kwargs
    ):
        """单行APL的逻辑函数：检查所有子条件并且输出结果"""
        result_box = []
        tick = kwargs.get("tick", None)
        preload_data = kwargs.get("preload_data", None)
        if self.apl_unit_type == "action.atk_response+=":
            """进攻响应APL的前置条件处理"""
            pass
        if not self.sub_conditions_unit_list:
            """无条件直接输出True"""
            return True, result_box
        from sim_progress.Preload.APLModule.SubConditionUnit import BaseSubConditionUnit

        for sub_units in self.sub_conditions_unit_list:
            if not isinstance(sub_units, BaseSubConditionUnit):
                raise TypeError(
                    "ActionAPLUnit类的sub_conditions_unit_list中的对象构建不正确！"
                )
            result = sub_units.check_myself(
                found_char_dict, game_state, tick=tick, sim_instance=sim_instance
            )
            result_box.append(result)
            if not result:
                return False, result_box
        else:
            return True, result_box

    def check_atk_response_conditions(self, preload_data: "PreloadData"):
        """检查进攻响应的前置条件是否满足"""
        if not preload_data.atk_manager.attacking:
            raise ValueError(
                f"在非进攻响应模式下，错误启用了进攻响应APL：{self.priority}"
            )
        if preload_data.atk_manager.is_answered:
            return False
        # TODO: 111111111111111111
