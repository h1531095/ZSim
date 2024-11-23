from Buff import Buff
import sys


class IceJadeTeaPotExtraDMGBonus(Buff.BuffLogic):
    """
    青衣专武>=15层时的额外增伤触发判定。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        main_module = sys.modules['__main__']
        Judge_list_set = main_module.init_data.Judge_list_set
        for i in range(len(Judge_list_set)):
            if Judge_list_set[i][1] == '玉壶青冰':
                self.user = Judge_list_set[i][0]
                break

    def special_judge_logic(self):
        main_module = sys.modules['__main__']
        DYNAMIC_BUFF_DICT = main_module.global_stats.DYNAMIC_BUFF_DICT
        for buffs in DYNAMIC_BUFF_DICT[self.user]:
            if not isinstance(buffs, Buff):
                raise TypeError(f'所检测的{buffs}不是Buff！')
            if '玉壶青冰-普攻加冲击' in buffs.ft.index:
                if buffs.dy.count >= 15:
                    return True
                else:
                    return False
            else:
                print(f'目前角色并未触发青衣专武的第一特效！')
                return False









