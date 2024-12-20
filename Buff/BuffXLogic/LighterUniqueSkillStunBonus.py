from Buff import Buff
from Buff.JudgeTools import find_char
from Character.Lighter import Lighter
import sys


class LighterUniqueSkillStunBonus(Buff.BuffLogic):
    """
    该buff是复杂判断 + 复杂生效双代码控制。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        self.xstart = self.special_start_logic
        self.last_morale = 40
        self.last_morale_delta = 0
        self.buff_count = 0
        self.char_lighter = None

    def special_judge_logic(self):
        """
        调用这个方法的位置，应该是buff_0的xjudge，所以，有效的self.buff_count也是存在buff_0里面的。
        """
        module_main = sys.modules['__main__']
        char_list = module_main.char_data.char_obj_list
        if self.char_lighter is None:
            self.char_lighter = find_char(1161, char_list)
        if self.char_lighter.morale > 10000:
            raise ValueError(f'snow又写错了')
        if self.last_morale > self.char_lighter.morale:
            # print(f'上一次士气{self.last_morale}；这一次士气{self.char_lighter.morale}')
            self.last_morale_delta = (self.last_morale - self.char_lighter.morale)/100
            self.buff_count = self.last_morale_delta
            self.last_morale = self.char_lighter.morale
            #   暂时假设不向下取整。
            return True
        else:
            self.last_morale = self.char_lighter.morale
            return False

    def special_start_logic(self):
        """
        这个方法需要在xjudge通过之后调用，此时调用的是buff_new的xeffect。
        所以这里需要向buff_0获取它的的层数。
        也就是buff_0.logic.buff_count
        """
        module_main = sys.modules['__main__']
        sub_exist_buff_dict = module_main.load_data.exist_buff_dict['莱特']
        buff_0 = sub_exist_buff_dict[self.buff_instance.ft.index]
        buff_i = self.buff_instance
        buff_i.dy.active = True
        tick = module_main.tick
        self.buff_count = buff_0.logic.buff_count
        buff_i.dy.count = min(buff_0.dy.count + self.buff_count, buff_0.ft.maxcount)
        buff_i.dy.startticks = tick
        buff_i.dy.endticks = tick + buff_i.ft.maxduration
        buff_i.dy.is_changed = True
        buff_i.update_to_buff_0(buff_0)

