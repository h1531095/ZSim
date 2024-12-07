from Buff import Buff
from Buff import JudgeTools
import sys


class MiyabiCoreSkill_FrostBurn(Buff.BuffLogic):
    """
    该buff是雅的核心被动中的【霜灼】，【霜灼】的进入机制是，随着烈霜属性异常触发，同步触发。
    执行这一步的是：update_anomaly函数，该函数会在烈霜属性积蓄条满的时候，
    根据bar.accompany_debuff中记录的str，去添加同名debuff。
    """

    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xexit = self.special_exit_logic
        self.last_frostbite = False

    def special_exit_logic(self):
        """
        霜灼buff的退出机制是检测到霜寒的下降沿就退出
        """
        main_module = sys.modules['__main__']
        enemy = main_module.schedule_data.enemy
        frostbite_now = enemy.dynamic.frostbite
        frostbite_statement = [self.last_frostbite, frostbite_now]
        mode_func = lambda a, b: a is True and b is False
        result = JudgeTools.detect_edge(frostbite_statement, mode_func)
        self.last_frostbite = frostbite_now
        return result



