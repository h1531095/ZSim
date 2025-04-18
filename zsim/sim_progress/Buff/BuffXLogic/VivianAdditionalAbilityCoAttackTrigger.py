from sim_progress.Buff import Buff, JudgeTools, check_preparation, find_tick


class VivianAdditionalAbilityCoAttackTriggerRecord:
    def __init__(self):
        self.char = None
        self.last_update_anomaly = None     # 上次更新的异常。
        self.cd = 30            # 内置CD0.5秒
        self.last_update_tick = 0       # 上次更新时间
        self.preload_data = None


class VivianAdditionalAbilityCoAttackTrigger(Buff.BuffLogic):
    def __init__(self, buff_instance):
        """薇薇安组队被动中的协同攻击触发器"""
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
            self.buff_0.history.record = VivianAdditionalAbilityCoAttackTriggerRecord()
        self.record = self.buff_0.history.record

    def special_judge_logic(self, **kwargs):
        """检测到属性异常传入后，进行判定。如果新的异常，则放行。"""
        self.check_record_module()
        self.get_prepared(char_CID=1331, preload_data=1)
        anomaly_bar = kwargs.get('anoamly_bar', None)
        if anomaly_bar is None:
            return False
        from sim_progress.AnomalyBar import AnomalyBar
        if not isinstance(anomaly_bar, AnomalyBar):
            raise TypeError(f"{self.buff_instance.ft.index}的xjudge函数获取的{anomaly_bar}不是AnomalyBar类！")
        # 如果是首次传入的属性异常类，则直接放行。
        tick = find_tick()
        if self.record.last_update_anomaly is None:
            self.record.last_update_anomaly = anomaly_bar
            self.record.last_update_tick = tick
            return True

        # 如果是同一异常，则不放行。
        if anomaly_bar.UUID == self.record.last_update_anomaly.UUID:
            return False

        # CD没转好，不触发。
        if tick - self.record.last_update_tick < self.record.cd:
            return False

        self.record.last_update_anomaly = anomaly_bar
        self.record.last_update_tick = tick
        return True

    def special_effect_logic(self, **kwargs):
        """一旦Xjudge放行，那么就执行本函数，试图生成一次生花。"""
        self.check_record_module()
        self.get_prepared(char_CID=1361, preload_data=1)
        coattack_skill_tag = self.record.char.feather_manager.spawn_coattack()
        if coattack_skill_tag is None:
            return
        input_tuple = (coattack_skill_tag, False)
        self.record.preload_data.external_add_skill(input_tuple)
        print(f'监听到队友触发了新的异常{self.record.last_update_anomaly.activated_by}，薇薇安触发了一次落雨生花！')








