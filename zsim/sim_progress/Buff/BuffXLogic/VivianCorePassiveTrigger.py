from sim_progress.Buff import Buff, JudgeTools, check_preparation, find_tick
from sim_progress.ScheduledEvent.Calculator import MultiplierData as Mul, Calculator as Cal
import math


class VivianCorePassiveTriggerRecord:
    def __init__(self):
        self.char = None
        self.preload_data = None
        self.last_update_anomaly = None
        self.enemy = None
        self.dynamic_buff_list = None
        self.sub_exist_buff_dict = None


class VivianCorePassiveTrigger(Buff.BuffLogic):
    def __init__(self, buff_instance):
        """薇薇安的核心被动触发器"""
        super().__init__(buff_instance)
        self.buff_instance = buff_instance
        self.buff_0 = None
        self.record = None
        self.xjudge = self.special_judge_logic
        self.xeffect = self.special_effect_logic
        self.ANOMALY_RATIO_MUL = {
            0: 0.0075,
            1: 0.08,
            2: 0.0108,
            3: 0.032,
            4: 0.0615,
            5: 0.0108
        }

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
        from sim_progress.AnomalyBar import AnomalyBar, AnomalyBarClass
        if anomaly_obj is None:
            return False
        if isinstance(anomaly_obj, AnomalyBar):
            if self.record.last_update_anomaly is None:
                self.record.last_update_anomaly = anomaly_obj
                return True
            if id(anomaly_obj) == id(self.record.last_update_anomaly):
                return False
            else:
                self.record.last_update_anomaly = anomaly_obj
                return True
        else:
            return False

    def special_effect_logic(self, **kwargs):
        """当Xjudge检测到AnomalyBar传入时通过判定，并且执行xeffect"""
        self.check_record_module()
        self.get_prepared(char_CID=1361, preload_data=1, dynamic_buff_list=1, enemy=1, sub_exist_buff_dict=1)
        from sim_progress.AnomalyBar import AnomalyBar
        copyed_anomaly = AnomalyBar.create_new_from_existing(self.record.last_update_anomaly)
        # copyed_anomaly = self.record.last_update_anomaly
        event_list = JudgeTools.find_event_list()
        mul_data = Mul(self.record.enemy, self.record.dynamic_buff_list, self.record.char)
        ap = Cal.AnomalyMul.cal_ap(mul_data)
        from sim_progress.AnomalyBar.CopyAnomalyForOutput import DirgeOfDestinyAnomaly
        dirge_of_destiny_anomaly = DirgeOfDestinyAnomaly(copyed_anomaly, active_by='1331')
        ratio = self.ANOMALY_RATIO_MUL.get(copyed_anomaly.element_type)
        final_ratio = math.floor(ap/10) * ratio
        dirge_of_destiny_anomaly.anomaly_dmg_ratio = final_ratio
        event_list.append(dirge_of_destiny_anomaly)
