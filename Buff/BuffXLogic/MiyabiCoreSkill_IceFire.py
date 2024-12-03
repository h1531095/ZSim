from Buff import Buff
import sys


class MiyabiCoreSkill_IceFire(Buff.BuffLogic):
    """
    该buff是雅的核心被动中的【冰焰】，冰焰在判断TrigerBuffLevel的同时，
    还需要检索当前enemy_debuff_list中是否含有【霜灼】，如果有就返回False
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        self.xexit = self.special_exit_logic

    def special_judge_logic(self):
        main_module = sys.modules['__main__']
        enemy = main_module.schedule_data.enemy
        action_stack = main_module.load_data.action_stack


    def special_exit_logic(self):
        pass