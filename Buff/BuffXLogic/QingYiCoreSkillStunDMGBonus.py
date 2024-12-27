from Buff import Buff, JudgeTools

class Record():
    def __init__(self):
        self.last_update_stun = False
        self.last_update_skill_tag = None




class QingYiCoreSkillStunDMGBonus(Buff.BuffLogic):
    """
    青衣的核心被动：[羁服]——失衡易伤以及连携技增伤；
    该buff有两个模块，分别是：XHit以及Xexit
    Xhit根据当前的Tag来控制层数的变化；
    而Xexit则在检测到失衡状态的下降沿时执行，输出True
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xhit = self.special_hit_logic
        self.xexit = self.special_exit_logic
        self.buff_0 = None
        self.char = None
        self.enemy = None

    def special_hit_logic(self):
        self.check_preparation()
        action_stack = JudgeTools.find_stack()
        action_now = action_stack.peek()
        tick_now = JudgeTools.find_tick()
        self.buff_instance.simple_start()
        if action_now.mission_tag == '1300_SNA_1':
            pass
        elif action_now.mission_tag == '1300_SNA_2':
            pass

    def special_exit_logic(self):
        self.check_preparation()
        pass

    def check_preparation(self):
        if self.char is None:
            self.char = JudgeTools.find_char_from_CID(1300)
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict()['青衣'][self.buff_instance.ft.index]
        if self.enemy is None:
            self.enemy = JudgeTools.find_enemy()
        if self.buff_0.history.record is None:
            self.buff_0.history.record = Record()
