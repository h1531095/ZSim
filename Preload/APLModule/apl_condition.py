

special_resource_name_dict = {
    1091: "frosty"
}


class APLCondition:
    """
    apl代码的条件解析函数，负责将打包好的apl代码，翻译为各种条件进行解析，并返回布尔值。
    """
    def __init__(self, game_state: dict):
        self.game_state = game_state
        self.found_char_dict = {}           # 用于装角色实例，键值是CID

    def evaluate(self, sub_action_dict: dict):
        char_CID = sub_action_dict['CID']
        char = self.find_char(char_CID)
        action_name = sub_action_dict['action']
        condition = sub_action_dict['condition']
        if char_CID != action_name[:3]:
            raise ValueError(f'动作名称和角色的CID不同！')

        # 示例条件解析逻辑
        if "energy" in condition:
            required = int(condition.split(">=")[-1])
            return self.game_state["energy"] >= required
        elif "resource" in condition:

            pass
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
        if CID in self.found_char_dict.keys():
            return self.found_char_dict[CID]
        for char in self.game_state["char_data"].char_obj_list:
            if char.CID == CID:
                self.found_char_dict[char.CID] = char
                return char
        else:
            raise ValueError(f'未找到CID为{CID}的角色！')

def comparison_like_conditions_trans(condition: str):
    pass


