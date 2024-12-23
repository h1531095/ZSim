from Buff import Buff, JudgeTools
import sys


class BranchBladeSongCritRateBonus(Buff.BuffLogic):
    def __init__(self, buff_instance):
        """
        该buff是新冰4的第二特效，需要检测冻结和碎冰效果。
        也就是enemy.dynamic.frozen的状态，只要发生改变，就可以触发。

        """
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xjudge = self.special_judge_logic
        self.last_tick_freez_statement = 0, False
        self.enemy = None
        self.main_module = None

    def special_judge_logic(self):
        if self.main_module is None:
            self.main_module = JudgeTools.find_main()
        if self.enemy is None:
            self.enemy = JudgeTools.find_enemy()
        tick = self.main_module.tick
        if self.enemy.dynamic.frozen is None:
            output = False
        else:
            output = self.enemy.dynamic.frozen
        this_tick_freez_statement = output

        if this_tick_freez_statement != self.last_tick_freez_statement[1]:
            self.last_tick_freez_statement = tick, this_tick_freez_statement
            return True
        else:
            self.last_tick_freez_statement = tick, this_tick_freez_statement
            return False
