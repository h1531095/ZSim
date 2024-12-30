from Buff import Buff, JudgeTools
from ScheduledEvent import Calculator
from ScheduledEvent.Calculator import MultiplierData
import sys


class LighterExtraSkill_IceFireBonus(Buff.BuffLogic):
    """
    这个buff的特性是：能叠20层，每层起码有1.25%冰火增伤。但是，每次层数更新时，都会检测冲击力，
    冲击力超过170的部分，都会以0.025%的数值增幅到这个1.25%的基础数值上。

    模型转换：
    以0.25%为一层，本buff最多300层。
    buff本身层数分为两种，一种为虚层（fake_count），另一种为实层（real_count）。
    实层根据命中次数，每次5层（共1.25%）稳定增加，每次实层更新后（self.update_to_buff0，该函数无法调用，需要手动)
    那么有效叠加次数：hit_count = real_count / 5，而且这个一定是int。
    根据当前冲击力超过170的部分，算出每个effect_count所享受的虚层增幅fake_count_delta : （当前冲击力-170）/10，该数值可以是个小数
    实层传回buff_0的专用字段 buff.history.real_count 保存，下一次再拿。
    本tick的实际生效层数，也就是最后记录到self.dy.count 的算法是：
    self.dy.count = min(real_count + hit_count * fake_count_delta, 300)
    下一个ticks，虚层清空，重新计算，实层重新从buff_0拿过来\
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xhit = self.special_hit_logic
        self.main_module = None
        self.char = None
        self.enemy = None
        self.dynamic_buff_list = None
        self.exist_buff_dict = None

    def special_hit_logic(self):
        if self.main_module is None:
            self.main_module = sys.modules['__main__']
        if self.enemy is None:
            self.enemy = JudgeTools.find_enemy()
        if self.dynamic_buff_list is None:
            self.dynamic_buff_list = JudgeTools.find_dynamic_buff_list()
        if self.char is None:
            self.char = JudgeTools.find_char_from_CID(1161)
        mul_data = MultiplierData(self.enemy, self.dynamic_buff_list, self.char)
        buff_0 = self.main_module.load_data.exist_buff_dict['莱特'][self.buff_instance.ft.index]
        buff_i = self.buff_instance
        buff_i.dy.active = True
        buff_i.dy.startticks = self.main_module.tick
        buff_i.dy.endticks = self.main_module.tick + buff_i.ft.maxduration

        real_count = buff_0.history.real_count
        real_count = min(real_count + 5, 100)
        buff_0.history.real_count = real_count
        """
        先处理real_count的逻辑，最多100层（叠加20次）
        """
        stun_value = Calculator.StunMul.cal_imp(mul_data)
        fake_count_delta = max((stun_value - 170)/10, 0)
        sum_fake_count = real_count / 5 * fake_count_delta
        buff_i.dy.count = min(real_count + sum_fake_count, 300)
        buff_i.update_to_buff_0(buff_0)
        # print('buff_i：', main_module.tick, buff_i.dy.active, buff_i.dy.startticks, buff_i.dy.endticks, real_count, sum_fake_count)
        # print('buff_0：', buff_0.dy.active, buff_0.dy.startticks, buff_0.dy.endticks, buff_0.history.real_count)



