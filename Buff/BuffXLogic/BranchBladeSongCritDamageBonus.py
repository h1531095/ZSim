from Buff import Buff, JudgeTools
from ScheduledEvent import Calculator
from ScheduledEvent.Calculator import MultiplierData


class BranchBladeSongCritDamageBonus(Buff.BuffLogic):
    """
    该buff是新冰4件套中的第一特效：异常掌控>=115就会触发。
    由于不能实现“异常掌控>=115时候，将buff.ft.alltime修改为True的操作，
    所以只能让该buff在每个动作都检测，然后每个动作都触发，用来平替alltime。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        self.equipper = None
        self.enemy = None
        self.dynamic_buff_list = None
        self.char = None

    def special_judge_logic(self):
        if self.equipper is None:
            self.equipper = JudgeTools.find_equipper("折枝剑歌")
        if self.char is None:
            char_list = JudgeTools.find_char_list()
            self.char = JudgeTools.find_char_from_name(self.equipper, char_list)
        if self.enemy is None:
            self.enemy = JudgeTools.find_enemy()
        if self.dynamic_buff_list is None:
            self.dynamic_buff_list = JudgeTools.find_dynamic_buff_list()
        mul_data = MultiplierData(self.enemy, self.dynamic_buff_list, self.char)
        am = Calculator.AnomalyMul.cal_am(mul_data)
        if am >= 115:
            return True
        return False






