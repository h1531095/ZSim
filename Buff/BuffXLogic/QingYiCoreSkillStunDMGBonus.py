from Buff import Buff, JudgeTools


class Record:
    """
    记录信息的类。从青衣开始，这些类要统一管理。
    """
    def __init__(self):
        self.pre_saved_counts = 0
        self.last_update_stun = False
        self.last_update_skill_tag = None
        # self.last_update_SNA_count = 5


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
        self.xstart = self.special_start_logic
        self.xexit = self.special_exit_logic
        self.sub_exist_buff_dict = None
        self.buff_0 = None
        self.char = None
        self.enemy = None

    def special_start_logic(self):
        """
        检测到当前的action_stack，判断它们的mission_tag
        SNA_1叠1层， 且预叠1层；
        SNA_2叠5层，且追加叠加所有的预叠层数。
        """
        self.check_preparation()
        action_stack = JudgeTools.find_stack()
        action_now = action_stack.peek()
        tick_now = JudgeTools.find_tick()
        self.buff_instance.simple_start(tick_now, self.sub_exist_buff_dict)
        self.buff_0.dy.count -= 1
        self.buff_instance.dy.count = self.buff_0.dy.count
        if action_now.mission_tag == '1300_SNA_1':
            self.buff_instance.dy.count += 1
            self.buff_0.history.record.pre_saved_counts += 1
            if self.buff_0.history.record.pre_saved_counts > 5:
                raise ValueError(f'1300_SNA_1提供的预叠层数已经超过了5，当前为：{self.buff_0.history.record.pre_saved_counts}')
        elif action_now.mission_tag == '1300_SNA_2':
            self.buff_instance.dy.count += 5
            self.buff_instance.dy.count += self.buff_0.history.record.pre_saved_counts
            self.buff_0.history.record.pre_saved_counts = 0
        self.buff_instance.dy.count = min(self.buff_instance.dy.count, 20)
        self.buff_instance.update_to_buff_0(self.buff_0)

    def special_exit_logic(self):
        """
        退出逻辑：检测到失衡的下降沿。
        """
        self.check_preparation()
        mode_func = lambda a, b: a is True and b is False
        stun_statement_tuple = self.buff_0.history.record.last_update_stun, self.enemy.dynamic.stun
        if JudgeTools.detect_edge(stun_statement_tuple, mode_func):
            self.buff_0.history.record.last_update_stun = self.enemy.dynamic.stun
            return True
        self.buff_0.history.record.last_update_stun = self.enemy.dynamic.stun
        return False

    def check_preparation(self):
        if self.char is None:
            self.char = JudgeTools.find_char_from_CID(1300)
        if self.sub_exist_buff_dict is None:
            self.sub_exist_buff_dict = JudgeTools.find_exist_buff_dict()['青衣']
        if self.buff_0 is None:
            self.buff_0 = self.sub_exist_buff_dict[self.buff_instance.ft.index]
        if self.enemy is None:
            self.enemy = JudgeTools.find_enemy()
        if self.buff_0.history.record is None:
            self.buff_0.history.record = Record()
