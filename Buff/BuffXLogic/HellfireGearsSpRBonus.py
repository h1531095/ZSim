from Buff import Buff, JudgeTools


class HellfireGearsSpRBonus(Buff.BuffLogic):
    """
    燃狱齿轮的后台回能。需要在初始化的时候就获取角色和武器配置列表
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        self.xexit = self.special_exit_logic
        self.init_data = None
        self.equipper = None

    def special_judge_logic(self):
        if self.init_data is None:
            self.init_data = JudgeTools.find_init_data()
        if self.equipper is None:
            self.equipper = JudgeTools.find_equipper("燃狱齿轮")
        name_box = self.init_data.name_box
        if name_box[0] != self.equipper:
            return True
        else:
            return False

    def special_exit_logic(self):
        name_box = self.init_data.name_box
        if name_box[0] == self.equipper:
            return True
        else:
            return False





