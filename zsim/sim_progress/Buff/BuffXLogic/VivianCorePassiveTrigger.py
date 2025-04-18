from sim_progress.Buff import Buff, JudgeTools, check_preparation, find_tick


class VivianCorePassiveTriggerRecord:
    def __init__(self):
        self.char = None
        self.last_update_anomaly = None


class VivianCorePassiveTrigger(Buff.BuffLogic):
    def __init__(self, buff_instance):
        """薇薇安的核心被动触发器"""
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.buff_0 = None
        self.record = None
        self.xjudge = self.special_judge_logic
        self.xeffect = self.special_effect_logic

    def get_prepared(self, **kwargs):
        return check_preparation(self.buff_0, **kwargs)

    def check_record_module(self):
        if self.buff_0 is None:
            self.buff_0 = JudgeTools.find_exist_buff_dict()['薇薇安'][self.buff_instance.ft.index]
        if self.buff_0.history.record is None:
            self.buff_0.history.record = VivianCorePassiveTriggerRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        """
        薇薇安的核心被动触发器：
        触发机制为：全队任意角色触发属性异常的第一跳时，构造一个新的属性异常放到Evenlist中
        """
        self.check_record_module()
        self.get_prepared(char_CID=1331)
        anomaly_obj = kwargs.get('anomaly_bar', None)
        from sim_progress.AnomalyBar.CopyAnomalyForOutput import DirgeOfDestinyAnomaly
        from sim_progress.AnomalyBar import AnomalyBar
        if anomaly_obj is None:
            return False
        if isinstance(anomaly_obj, AnomalyBar):
            return True
        else:
            return False

    def special_effect_logic(self, **kwargs):

        self.check_record_module()
        self.get_prepared(char_CID=1361, preload_data=1)
        coattack_skill_tag = self.record.char.feather_manager.spawn_coattack()
        if coattack_skill_tag is None:
            return
        event_list = JudgeTools.find_event_list()







