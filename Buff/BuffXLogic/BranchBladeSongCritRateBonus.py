from Buff import Buff
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
        self.main = None

    def get_main_module(self):
        if self.main is None:
            self.main = sys.modules["__main__"]
        return self.main

    def special_judge_logic(self):
        main_module = self.get_main_module()
        enemy = main_module.schedule_data.enemy
        tick = main_module.tick
        if enemy.dynamic.frozen is None:
            output = False
        else:
            output = enemy.dynamic.frozen
        this_tick_freez_statement = output

        if this_tick_freez_statement != self.last_tick_freez_statement[1]:
            self.last_tick_freez_statement = tick, this_tick_freez_statement
            return True
        else:
            self.last_tick_freez_statement = tick, this_tick_freez_statement
            return False
