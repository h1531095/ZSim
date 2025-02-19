
from .sub_evaluation_unit import sub_evaluation_unit
from sim_progress.Character import Character


class APLCondition:
    """
    apl代码的条件解析函数，负责将打包好的apl代码，翻译为各种条件进行解析，并返回布尔值。
    """
    def __init__(self, game_state: dict):
        self.game_state = game_state
        self.found_char_dict: dict[int, Character] = {}           # 用于装角色实例，键值是CID
        self.condition_inventory: dict[int, sub_evaluation_unit] = {}            # 用于装已经解析过的apl子条件实例。
        # self._access_cache = lru_cache(maxsize=100)(self._create_accessor)

    def evaluate(self, condition: list | None, priority: int):
        if priority not in self.condition_inventory:
            self.condition_inventory[priority] = sub_evaluation_unit(priority, condition)
        logic_unit = self.condition_inventory[priority]
        if not isinstance(logic_unit, sub_evaluation_unit):
            raise ValueError(f'condition_inventory中的Value不是sub_evaluation_unit实例')
        result = logic_unit.run_myself(self.found_char_dict, self.game_state)
        # print(f'当前优先级为：{priority}, 当前正在处理的条件为：{condition}, 结果为：{result}')
        return result

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
