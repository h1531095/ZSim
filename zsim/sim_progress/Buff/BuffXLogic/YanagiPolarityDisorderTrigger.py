from sim_progress.Buff import Buff, JudgeTools, check_preparation


class YanagiPolarityDisorderTriggerRecord:
    def __init__(self):
        self.char = None


class YanagiPolarityDisorderTrigger(Buff.BuffLogic):
    """
    柳的极性紊乱的触发器。
    极性紊乱会在强化E下落攻击和Q的最后一个Hit触发，
    若是一个招式内同时触发了感电和极性紊乱，则应该先结算感电，再结算极性紊乱；
    根据目前ZSim的结构，属性异常检测、属性异常更新、Buff判断循环启动这几个步骤的顺序应该为：
    Buff判断循环启动 ——> 触发器启动 ——> 属性异常更新——> 技能伤害计算——> 异常条更新
    所以，如果在极性紊乱更新的Tick，同时触发了新的属性异常，
    """
    def __init__(self, buff_instance):
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.xjudge = self.special_judge_logic
        self.buff_0 = None
        self.record = None

    def get_prepared(self, **kwargs):
        return check_preparation(self.buff_0, **kwargs)

    def check_record_module(self):
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict()['柳'][self.buff_instance.ft.index]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = YanagiPolarityDisorderTriggerRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        """
        """
        self.check_record_module()
        self.get_prepared(char_CID=1221)


