from Buff import Buff
from Enemy import Enemy
import sys


class LighterUniqueSkillStunTimeLimitBonus(Buff.BuffLogic):
    """
    该buff的退出逻辑特殊，失衡结束就会直接退出。

    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xexit = self.special_exit_logic
        self.last_stun_statement = False
    def special_exit_logic(self):
        """
        获取当前失衡值，和上一次失衡值对比。
        """
        main_module = sys.modules['__main__']
        enemy = main_module.schedule_data.enemy
        if not isinstance(enemy, Enemy):
            raise TypeError(f'获取的enemy类型不对')
        if self.last_stun_statement and not enemy.dynamic.stun:
            self.last_stun_statement = enemy.dynamic.stun
            return True
        else:
            self.last_stun_statement = enemy.dynamic.stun
            return False






