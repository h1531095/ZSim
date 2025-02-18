import re
from functools import lru_cache
from typing import Any, Callable
from define import SWAP_CANCEL
from sim_progress.Character import Character


class APLCondition:
    """
    apl代码的条件解析函数，负责将打包好的apl代码，翻译为各种条件进行解析，并返回布尔值。
    """
    def __init__(self, game_state: dict):
        self.game_state = game_state
        self.found_char_dict: dict[int, Character] = {}           # 用于装角色实例，键值是CID

        # self._access_cache = lru_cache(maxsize=100)(self._create_accessor)

    # def _parse_path(self, path: str):
    #     """解析混合属性/字典的路径 (如 enemy.anomaly_bars_dict[5])"""
    #     pattern = re.compile(r'(\w+)(?:\[([^]]+)])?\.?')
    #     return pattern.findall(path)  # 返回 [(attr, key), ...]
    #
    # def _create_accessor(self, full_path: str) -> Callable:
    #     """生成支持字典访问的访问器"""
    #     steps = self._parse_path(full_path)
    #
    #     def accessor(obj):
    #         current = obj
    #         for attr, key in steps:
    #             current = getattr(current, attr, None)
    #             if key:  # 处理字典键访问
    #                 key = int(key) if key.isdigit() else key.strip("\"'")
    #                 current = current.get(key, None) if hasattr(current, 'get') else None
    #             if current is None:
    #                 break
    #         return current
    #
    #     return accessor

    def evaluate(self, sub_action_dict: dict, condition: str):
        char_CID: int = int(sub_action_dict['CID'])
        char = self.find_char(char_CID)
        action_name = sub_action_dict['action']
        if "auto_NA" not in action_name and str(char_CID) != action_name[:4]:
            raise ValueError(f'当前的APL代码是：{condition}，动作名称和角色的CID不同！')
        # 示例条件解析逻辑
        judge_code: str | tuple[str, str]
        if condition is None:
            return True
        if "status" in condition:
            if "status.char" in condition:
                checked_CID = condition.split(":")[0].split("_")[-1].strip()
                judge_code = condition.split(":")[-1].strip()
                return self.evaluate_other_char_status(int(checked_CID), judge_code)
            else:
                judge_code = condition.split(":")[-1].strip()
                # EXAMPLE：enemy.dynamic.stun==True
                status = self.get_dynamic_status(judge_code)
                return status
        elif "buff" in condition:
            if "count" in condition:
                judge_code = condition.split(":")[-2].strip(), condition.split(":")[-1].strip()
                # EXAMPLE：judge_code = (buff.ft.index, condition)
                return self.evaluate_buff_count_conditions(char_CID, judge_code)
            elif "exist" in condition:
                buff_index = condition.split(":")[-1].strip()
                if self.find_buff(char, buff_index) is None:
                    return False
                else:
                    return True
        elif "energy" in condition:
            compared_value: tuple | int | float = char.sp
            return compare_method(compared_value, condition)
        elif "resource" in condition:
            compared_value = char.get_resources()
            return compare_method(compared_value, condition)
        elif "after" in condition:
            required_action = condition.split(":")[-1].strip()
            last_action = self.get_last_action()
            return last_action == required_action
        elif "decibel" in condition:
            compared_value = char.decibel
            return compare_method(compared_value, condition)
        elif "stun" in condition:
            raise NotImplementedError("[APL]: 暂不支持stun判定！")
        elif "health_pct" in condition:
            raise NotImplementedError("[APL]: 暂不支持health_pct判定！")
        elif "time" in condition:
            raise NotImplementedError("[APL]: 暂不支持time判定！")
    
        return False

    def find_char(self, CID: int) -> Character:
        """
        根据提供的CID，找到对应的char，并且返回、保存在self.found_char_dict中。
        每次调用时，会先检查是否在self.found_char_dict中。如果找不到，再扔出去。
        """
        if CID in self.found_char_dict.keys():
            return self.found_char_dict[CID]
        char: Character
        for char in self.game_state["char_data"].char_obj_list:
            if char.CID == int(CID):
                self.found_char_dict[char.CID] = char
                return char
        else:
            raise ValueError(f'未找到CID为{CID}的角色！')

    def get_last_action(self) -> str:
        """
        注意，这个函数获取的应该是上一个主动动作的名称，
        所以，这里调用的是preload_data.current_on_field_node
        """
        if SWAP_CANCEL:
            return self.game_state['preload'].preload_data.current_on_field_node_tag
        else:
            last_node = getattr(self.game_state['preload'].preload_data,'last_node', None)
            if last_node is None:
                return None
            output = last_node.skill_tag
            return output

    def get_dynamic_status(self, judge_code: str) -> bool:
        """
        用于获取各种状态的函数。
        由于eval函数是无法阅读上下文的，
        所以需要制定将self作为参数传进去，并且指定给“self”。
        """
        # Original Code:
        if "enemy" in judge_code:
            first_half = 'self.game_state["schedule_data"].'
            hole_string = first_half + judge_code
            return eval(hole_string, {}, {"self": self})
        else:
            return False

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
        # compare_methods_mapping = {
        #     '<': lambda a, b: a < b,
        #     '<=': lambda a, b: a <= b,
        #     '>': lambda a, b: a > b,
        #     '>=': lambda a, b: a >= b,
        #     '==': lambda a, b: a == b
        # }
        # print("Debugging 1st", target_value, '2nd', value)
        # return compare_methods_mapping[operator](target_value, type(target_value)(value))  # 保持类型一致

    @staticmethod
    def _judge_code_spliter(judge_code: str) -> tuple:
        """拆分为类似['enemy.hp', '<', '10']"""
        operators = ['<=', '<', '>=', '>', '==']
        for operator in operators:
            if operator in judge_code:
                path, value = judge_code.split(operator)
                return path, operator, value
        else:
            raise ValueError(f"[APL]: 无法识别的判定条件！")

    def evaluate_buff_count_conditions(self, char_CID, judge_code: tuple) -> bool:
        """
        该函数用于处理Buff类的判定条件，并最终输出布尔值。
        """
        buff_index = judge_code[0]
        char = self.find_char(char_CID)
        condition_code = judge_code[1]
        buff = self.find_buff(char, buff_index)
        if not buff:
            return False
        elif "count" in condition_code:
            compared_value = buff.dy.count
            return compare_method(compared_value, condition_code)
        else:
            raise NotImplementedError("[APL]: Buff条件判断暂不支持该类型！")

    def evaluate_other_char_status(self, CID: int, judge_code: str):
        """
        用来处理查询其他角色状态或是特殊资源的逻辑；
        """
        char = self.find_char(CID)
        hole_judge_code = 'char.' + judge_code
        return eval(hole_judge_code,  {}, {"char": char})

    def find_buff(self, char, buff_index):
        """
        根据buff的index来找到buff
        通常用于判断“当前是否有该Buff激活”
        """
        for buffs in self.game_state["global_stats"].DYNAMIC_BUFF_DICT[char.NAME]:
            if buffs.ft.index == buff_index:
                return buffs
        else:
            return None


@lru_cache(maxsize=128)
def compare_method(compared_value: tuple[str, str|int|float] | str | int | float, condition: str) -> bool:
    """
    这个函数是用来处理含有比较符号的内容的，比如 >= <= == !=
    compared_value: 被比较的值
    condition: 包含比较符号和目标值的字符串，例如 ">=10", "<5", "==3" 等
    return: 布尔值，表示比较结果
    """
    if isinstance(compared_value, tuple):
        """
        由于各角色的get_resources函数抛出的是一个tuple：(资源名，资源数值)
        所以，这里需要把数值拿出来
        """
        num_compared_value = try_eval_single_str(compared_value[1])
    else:
        num_compared_value = try_eval_single_str(compared_value)

    if '<=' in condition:  # 先判断包含两个字符的符号，避免匹配冲突
        required = int(eval(condition.split("<=")[-1].strip()))
        return num_compared_value <= required
    elif '>=' in condition:
        required = int(eval(condition.split(">=")[-1].strip()))
        return num_compared_value >= required
    elif '==' in condition:
        required = int(eval(condition.split("==")[-1].strip()))
        return num_compared_value == required
    elif '!=' in condition:
        required = int(eval(condition.split("!=")[-1].strip()))
        return num_compared_value != required
    elif '<' in condition:  # 单独判断单字符符号
        required = int(eval(condition.split("<")[-1].strip()))
        return num_compared_value < required
    elif '>' in condition:
        required = int(eval(condition.split(">")[-1].strip()))
        return num_compared_value > required
    else:
        raise ValueError(f'condition \"{condition}\" 中不含有有效的比较符号，不应该调用 compare_method 函数！')

def try_eval_single_str(compared_value: str | Any) -> Any:
    """
    尝试将字符串转化为数值（eval)，如果失败，则返回原字符串。
    """
    if isinstance(compared_value, str):
        num_compared_value = eval(compared_value)
    else:
        num_compared_value = compared_value
    return num_compared_value


