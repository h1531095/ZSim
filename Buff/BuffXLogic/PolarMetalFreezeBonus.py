from Buff import Buff
import sys


class PolarMetalFreezeBonus(Buff.BuffLogic):
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xjudge = self.special_judge_logic
        self.last_tick_freez_statement = 0, False

    def special_judge_logic(self):
        main_module = sys.modules['__main__']
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
