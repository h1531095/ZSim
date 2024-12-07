from Buff import Buff
from Buff import JudgeTools
from ScheduledEvent import Calculator
from ScheduledEvent.Calculator import MultiplierData
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
        self.xhit = self.special_hit_logic
        self.last_frostbite = False

    def special_judge_logic(self):
        """
        这个复杂判断逻辑需要同时检索当前技能的element_type，
        以及enemy的debuff_list有没有霜灼，
        两者都通过，才会return True
        """
        main_module = sys.modules['__main__']
        enemy = main_module.schedule_data.enemy
        action_stack = main_module.load_data.action_stack
        mission_now = action_stack.peek()
        debuff_list = enemy.dynamic.dynamic_debuff_list
        if mission_now.mission_node.skill.element_type != 5:
            return False
        else:
            for debuff in debuff_list:
                if not isinstance(debuff, Buff):
                    raise TypeError(f'{debuff}不是Buff类！')
                if debuff.ft.index == 'Buff-角色-雅-核心被动-霜灼':
                    return False
            else:
                return True


    def special_exit_logic(self):
        """
        冰焰buff的退出机制是检测到霜寒的上升沿就退出
        """
        main_module = sys.modules['__main__']
        enemy = main_module.schedule_data.enemy
        frostbite_now = enemy.dynamic.frostbite
        if frostbite_now is None:
            frostbite_now = False
        frostbite_statement = [self.last_frostbite, frostbite_now]
        print(frostbite_statement)
        mode_func = lambda a, b: a is False and b is True
        result = JudgeTools.detect_edge(frostbite_statement, mode_func)
        self.last_frostbite = frostbite_now
        # print(f'当前tick，冰焰退出情况：{result}')
        if result:
            print('ffffffff')
        return result


    def special_hit_logic(self):
        """
        冰焰的生效机制是：根据当前的暴击率，得出当前的Buff层数。
        这个效果本应该是随动的，不需要buff判定通过才改变层数，
        但是如果buff判定不通过，那么烈霜伤害，该buff层数的变动就没有实际意义，
        """
        main_module = sys.modules['__main__']
        char_list = main_module.char_data.char_obj_list
        enemy = main_module.schedule_data.enemy
        dynamic_buff = main_module.global_stats.DYNAMIC_BUFF_DICT
        buff_0 = main_module.load_data.exist_buff_dict['雅'][self.buff_instance.ft.index]
        buff_i = self.buff_instance
        buff_i.dy.active = True
        buff_i.dy.startticks = main_module.tick
        buff_i.dy.endticks = main_module.tick + buff_i.ft.maxduration
        for _ in char_list:
            if _.CID == 1091:
                character = _
                mul_data = MultiplierData(enemy, dynamic_buff, character)
                break
        else:
            raise ValueError(f'char_list中并未找到角色雅')
        cric_rate = Calculator.RegularMul.cal_crit_rate(mul_data)
        count = min(cric_rate, 0.8)*100
        # print(cric_rate, count)
        buff_i.dy.count = min(count, buff_0.ft.maxcount)
        buff_i.dy.is_changed = True
        buff_i.update_to_buff_0(buff_0)

