from Buff import Buff, JudgeTools
import sys


class IceJadeTeaPotExtraDMGBonus(Buff.BuffLogic):
    """
    青衣专武>=15层时的额外增伤触发判定。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        self.equipper = None

    def special_judge_logic(self):
        if self.equipper is None:
            self.equipper = JudgeTools.find_equipper("玉壶青冰")
        dynamic_buff_list = JudgeTools.find_dynamic_buff_list()
        # print([buffx.ft.index for buffx in dynamic_buff_list[self.equipper]])
        for buffs in dynamic_buff_list[self.equipper]:
            if not isinstance(buffs, Buff):
                raise TypeError(f'所检测的{buffs}不是Buff！')
            if '玉壶青冰-普攻加冲击' not in buffs.ft.index:
                continue
            if buffs.dy.count >= 15:
                return True
            else:
                return False









