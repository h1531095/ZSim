from Buff import Buff
import sys


class LighterUniqueSkillStunBonus(Buff.BuffLogic):
    """
    该buff是复杂判断 + 复杂生效双代码控制。

    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        self.xeffect = self.special_effect_logic
        self.last_morale = None

    def special_judge_logic(self):
        pass

    def special_effect_logic(self):
        pass

