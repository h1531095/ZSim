class APLCondition:
    """
    apl代码的条件解析函数，负责将打包好的apl代码，翻译为各种条件进行解析，并返回布尔值。
    """
    def __init__(self):
        self.game_state = None
        self.found_char_dict = {}           # 用于装角色实例，键值是CID

    def evaluate(self, sub_action_dict: dict, condition: str):
        char_CID = sub_action_dict['CID']
        char = self.find_char(char_CID)
        action_name = sub_action_dict['action']
        if char_CID != action_name[:4]:
            raise ValueError(f'动作名称和角色的CID不同！')

        # 示例条件解析逻辑
        if condition is None:
            return True
        elif "energy" in condition:
            compared_value = char.sp
            return compare_method(compared_value, condition)
        elif "resource" in condition:
            compared_value = char.get_resources()
            return compare_method(compared_value, condition)
        elif "buff" in condition:
            pass
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
        if self.game_state is None:
            self.get_game_state()
        if CID in self.found_char_dict.keys():
            return self.found_char_dict[CID]
        for char in self.game_state["char_data"].char_obj_list:
            if char.CID == int(CID):
                self.found_char_dict[char.CID] = char
                return char
        else:
            raise ValueError(f'未找到CID为{CID}的角色！')

    def get_game_state(self):
        import sys
        main_module = sys.modules['__main__']
        self.game_state = main_module.game_state

def compare_method(compared_value, condition: str):
    """
    这个函数是用来处理含有比较符号的内容的，比如 >= <= == !=
    compared_value: 被比较的值
    condition: 包含比较符号和目标值的字符串，例如 ">=10", "<5", "==3" 等
    return: 布尔值，表示比较结果
    """
    if '<=' in condition:  # 先判断包含两个字符的符号，避免匹配冲突
        required = int(condition.split("<=")[-1].strip())
        return compared_value <= required
    elif '>=' in condition:
        required = int(condition.split(">=")[-1].strip())
        return compared_value >= required
    elif '==' in condition:
        required = int(condition.split("==")[-1].strip())
        return compared_value == required
    elif '!=' in condition:
        required = int(condition.split("!=")[-1].strip())
        return compared_value != required
    elif '<' in condition:  # 单独判断单字符符号
        required = int(condition.split("<")[-1].strip())
        return compared_value < required
    elif '>' in condition:
        required = int(condition.split(">")[-1].strip())
        return compared_value > required
    else:
        raise ValueError(f'condition \"{condition}\" 中不含有有效的比较符号，不应该调用 compare_method 函数！')

