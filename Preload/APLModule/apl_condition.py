class APLCondition:
    """
    apl代码的条件解析函数，负责将打包好的apl代码，翻译为各种条件进行解析，并返回布尔值。
    """
    def __init__(self, game_state: dict):
        self.game_state = game_state
        self.found_char_dict = {}           # 用于装角色实例，键值是CID

    def evaluate(self, sub_action_dict: dict, condition: str):
        char_CID = sub_action_dict['CID']
        char = self.find_char(char_CID)
        action_name = sub_action_dict['action']
        if "auto_NA" not in action_name and char_CID != action_name[:4]:
            print(action_name)
            raise ValueError(f'动作名称和角色的CID不同！')

        # 示例条件解析逻辑
        if condition is None:
            return True
        elif "status" in condition:
            judge_code = condition.split(":")[-1].strip()
            # 例：enemy.dynamic.stun==True
            return self.get_dynamic_status(judge_code)
        elif "buff" in condition:
            judge_code = condition.split(":")[-2].strip(), condition.split(":")[-1].strip()
            # EXPLAIN：judge_code = (buff.ft.index, condition)
            return self.evaluate_buff_conditions(char_CID, judge_code)
        elif "energy" in condition:
            compared_value = char.sp
            return compare_method(compared_value, condition)
        elif "resource" in condition:
            compared_value = char.get_resources()
            return compare_method(compared_value, condition)
        elif "after" in condition:
            last_action = self.get_last_action()
            required_action = condition.split(":")[-1].strip()
            return last_action == required_action
        elif "decibel" in condition:
            compared_value = char.decibel
            return compare_method(compared_value, condition)
        elif "stun" in condition:
            pass
        elif "health_pct" in condition:
            pass
        elif "time" in condition:
            pass
        else:
            return False

    def find_char(self, CID):
        """
        根据提供的CID，找到对应的char，并且返回、保存在self.found_char_dict中。
        每次调用时，会先检查是否在self.found_char_dict中。如果找不到，再扔出去。
        """
        if CID in self.found_char_dict.keys():
            return self.found_char_dict[CID]
        for char in self.game_state["char_data"].char_obj_list:
            if char.CID == int(CID):
                self.found_char_dict[char.CID] = char
                return char
        else:
            raise ValueError(f'未找到CID为{CID}的角色！')

    def get_last_action(self):
        output = self.game_state['preload'].preload_data.last_node
        if output is None:
            return None
        return output.skill_tag

    def get_dynamic_status(self, judge_code: str):
        """
        用于获取各种状态的函数。
        由于eval函数是无法阅读上下文的，
        所以需要制定将self作为参数传进去，并且指定给“self”。
        """
        if "enemy" in judge_code:
            first_half = 'self.game_state["schedule_data"].'
            hole_string = first_half + judge_code
            return eval(hole_string, {}, {"self": self})

    def evaluate_buff_conditions(self, char_CID, judge_code: tuple) -> bool:
        """
        该函数用于处理Buff类的判定条件，并最终输出布尔值。
        """
        buff_index = judge_code[0]
        char = self.find_char(char_CID)
        condition_code = judge_code[1]
        buff = self.find_buff(char, buff_index)
        if buff is None:
            return False
        if "count" in condition_code:
            compared_value = buff.dy.count
            return compare_method(compared_value, condition_code)

    def find_buff(self, char, buff_index):
        for buffs in self.game_state["global_stats"].DYNAMIC_BUFF_DICT[char.NAME]:
            if buffs.ft.index == buff_index:
                return buffs
        else:
            return None





def compare_method(compared_value, condition: str):
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
        compared_value = compared_value[1]
    if '<=' in condition:  # 先判断包含两个字符的符号，避免匹配冲突
        required = int(eval(condition.split("<=")[-1].strip()))
        return compared_value <= required
    elif '>=' in condition:
        required = int(eval(condition.split(">=")[-1].strip()))
        return compared_value >= required
    elif '==' in condition:
        required = int(eval(condition.split("==")[-1].strip()))
        return compared_value == required
    elif '!=' in condition:
        required = int(eval(condition.split("!=")[-1].strip()))
        return compared_value != required
    elif '<' in condition:  # 单独判断单字符符号
        required = int(eval(condition.split("<")[-1].strip()))
        return compared_value < required
    elif '>' in condition:
        required = int(eval(condition.split(">")[-1].strip()))
        return compared_value > required
    else:
        raise ValueError(f'condition \"{condition}\" 中不含有有效的比较符号，不应该调用 compare_method 函数！')


