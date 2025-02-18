from sim_progress.Buff import Buff, JudgeTools


class PreciousFossilizedCoreStunBonusOver50Hp(Buff.BuffLogic):
    """
    这段代码是贵重骨核的复杂判断逻辑。
    敌人生命大于50%时生效。
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        # 初始化特定逻辑
        self.xjudge = self.special_judge_logic

    def special_judge_logic(self):
        enemy = JudgeTools.find_enemy()
        hp_pct = enemy.get_hp_percentage()
        if hp_pct >= 0.5:
            return True
        else:
            return False
