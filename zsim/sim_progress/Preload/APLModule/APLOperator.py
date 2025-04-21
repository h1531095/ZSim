from .APLUnit import APLUnit, ActionAPLUnit


class APLOperator:
    """APL执行器，负责运行对象化的APL代码，并返回布尔值。"""

    def __init__(self, all_apl_unit_list, game_state: dict):
        self.game_state = game_state
        self.found_char_dict = {}  # 用于装角色实例，键值是CID
        self.apl_unit_inventory: dict[
            int, APLUnit
        ] = {}  # 用于装已经解析过的apl子条件实例。
        for unit_dict in all_apl_unit_list:
            self.apl_unit_inventory[unit_dict["priority"]] = apl_unit_factory(unit_dict)

    def spawn_next_action(self, tick):
        """APL执行器的核心功能函数——筛选出优先级最高的下一个动作"""
        for priority, apl_unit in self.apl_unit_inventory.items():
            if isinstance(apl_unit, ActionAPLUnit):
                result, result_box = apl_unit.check_all_sub_units(
                    self.found_char_dict, self.game_state, tick=tick
                )
                if not result:
                    # if priority in [0, 1, 2]:
                    #     print(f'这次不通过的APL优先级为{priority}， 判定结果为：{result_box}')
                    continue
                else:
                    if apl_unit.break_when_found_action:
                        # print(f'APL找到了新的最高优先级的动作！优先级为：{apl_unit.priority}，输出动作：{apl_unit.result}')
                        return (
                            int(apl_unit.char_CID),
                            apl_unit.result,
                            apl_unit.priority,
                        )
                    else:
                        continue
        else:
            raise ValueError("没有找到符合要求的APL！")


def apl_unit_factory(apl_unit_dict):
    """构造APL子单元的工厂函数"""
    if apl_unit_dict["type"] == "action+=":
        return ActionAPLUnit(apl_unit_dict)
        # # Optimized Code:
        #
        # if "enemy" not in judge_code:
        #     return False
        # path, operator, value = self._judge_code_spliter(judge_code)
        # accessor = self._access_cache(path)  # 缓存访问器
        #
        # # 获取实际数值
        # target_value = accessor(self.game_state["schedule_data"])
        # if target_value is None:
        #     return False
        #
        # # 执行比较操作（可扩展更多运算符）

        # print("Debugging 1st", target_value, '2nd', value)
        # return compare_methods_mapping[operator](target_value, type(target_value)(value))  # 保持类型一致
