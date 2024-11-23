from Buff import Buff
import sys


class HellfireGearsSpRBonus(Buff.BuffLogic):
    """
    燃狱齿轮的后台回能。需要在初始化的时候就获取角色和武器配置列表
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        main_module = sys.modules['__main__']
        Judge_list_set = main_module.init_data.Judge_list_set
        for i in range(len(Judge_list_set)):
            if Judge_list_set[i][1] == '燃狱齿轮':
                self.user = Judge_list_set[i][0]
                break

    def special_judge_logic(self):
        main_module = sys.modules['__main__']
        name_box = main_module.init_data.name_box
        if name_box[0] != self.user:
            return True
        else:
            return False






