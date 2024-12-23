from Buff import Buff, JudgeTools


class SteamOven(Buff.BuffLogic):
    """
    这段代码是人为刀俎的生效逻辑。根据能量返回层数。
    由于该效果要求在能量扣除后还能继续存在8秒，且每一层效果单独结算持续时间，
    应在每次更新时，都实时检测当前能量，并更新buff.dy.built_in_buff_box中的所有list。
    更新方式不是替换，而是类似于栈。
    这里不需要管过期tuples的移除，只需要管溢出tuples的移除即可。
    注意，这个Buff的复杂判断逻辑永远是False，但是只输出True。
    不能用Alltime参数来平替，因为这样会导致在Update_Buff函数中，本Buff会提前被送出循环，而跳过清理过期tuples的步骤。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xjudge = self.special_judge_logic
        self.xeffect = self.special_effect_logic
        self.equipper = None


    def special_judge_logic(self):
        return True

    def special_effect_logic(self):
        if self.equipper is None:
            self.equipper = JudgeTools.find_equipper("人为刀俎")

