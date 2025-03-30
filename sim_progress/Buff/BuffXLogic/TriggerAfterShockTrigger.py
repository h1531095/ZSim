from sim_progress.Buff import Buff, JudgeTools, check_preparation, find_tick





class TriggerAfterShockTriggerRecord:
    def __init__(self):
        self.char = None
        self.preload_data = None
        self.after_shock_manager = None


class TriggerAfterShockTrigger(Buff.BuffLogic):

    def __init__(self, buff_instance):
        """扳机的协同攻击触发器"""
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.buff_0 = None
        self.record = None
        self.xjudge = self.special_judge_logic
        self.xhit = self.special_hit_logic

    def get_prepared(self, **kwargs):
        return check_preparation(self.buff_0, **kwargs)

    def check_record_module(self):
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict()['扳机'][self.buff_instance.ft.index]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = TriggerAfterShockTriggerRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        """
        触发器的xjudge函数，负责判断当前攻击是否能够触发协同攻击，主要包括
        （以下选项优先级未定）
        1、决意值的判定，决意值>消耗值，才允许触发
        2、检查协战状态的buff是否存在？？
        3、筛选触发条件
        """
        self.check_record_module()
        self.get_prepared(char_CID=1361, preload_data=1)
        loading_mission = kwargs.get('loading_mission', None)
        if loading_mission is None:
            raise ValueError(f'{self.buff_instance.ft.index}的xjudge函数中，传入的loading_mission为None！')
        from sim_progress.Load import LoadingMission
        if not isinstance(loading_mission, LoadingMission):
            raise TypeError
        tick = find_tick()
        if not loading_mission.is_hit_now(tick):
            return False



