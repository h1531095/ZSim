from sim_progress.Buff import Buff, JudgeTools


class IceJadeTeaPotExtraDMGBonus(Buff.BuffLogic):
    """
    青衣专武>=15层时的额外增伤触发判定。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic

    def special_judge_logic(self, **kwargs):
        equipper = JudgeTools.find_equipper("玉壶青冰")
        dynamic_buff_list = JudgeTools.find_dynamic_buff_list()
        for buffs in dynamic_buff_list[equipper]:
            if '玉壶青冰-普攻加冲击' not in buffs.ft.index:
                continue
            if buffs.dy.count >= 15:
                return True
            else:
                return False









