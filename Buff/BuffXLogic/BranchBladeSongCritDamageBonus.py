from Buff import Buff
from ScheduledEvent import Calculator
from ScheduledEvent.Calculator import MultiplierData
import sys


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
        self.main = None
        self.equipper = None

    def get_main_module(self):
        if self.main is None:
            self.main = sys.modules["__main__"]
        return self.main

    def special_judge_logic(self):
        main_module = self.get_main_module()

        if self.equipper is None:
            Judge_list_set = main_module.init_data.Judge_list_set
            for box in Judge_list_set:
                if box[2] == self.buff_instance.ft.bufffrom:
                    self.equipper = box[0]
                    break
        char_list = main_module.char_data.char_obj_list
        enemy = main_module.schedule_data.enemy
        dynamic_buff = main_module.global_stats.DYNAMIC_BUFF_DICT
        for _ in char_list:
            if _.NAME == self.equipper:
                character = _
                mul_data = MultiplierData(enemy, dynamic_buff, character)
                break
        else:
            raise ValueError(f'char_list中并未找到角色{self.equipper}')
        am = Calculator.AnomalyMul.cal_am(mul_data)
        if am >= 115:
            return True
        return False






