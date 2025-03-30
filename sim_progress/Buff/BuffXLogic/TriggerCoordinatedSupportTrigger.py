class CoordinatedSupportManager:
    """协战状态管理器"""
    def __init__(self):
        self.coordinated_support = False
        self.update_tick = 0
        self.end_tick = 0
        self.max_duration = 1200
        self.max_count = 10
        self.after_shock_tag = '1361_CoAttack_A'
        self.count = 0
        self.update_count_box = {2: 4, 6: 6}
        self.update_tick_box = {2: 480, 6: 720}

    def update_myself(self, tick: int, skill_node):
        """传入skill_node，更新自身状态"""
        if skill_node.skill_trigger_buff_level in [2, 6]:
            self.coordinated_support = True
            self.update_tick = tick
            if self.is_active(tick):
                '''如果更新的时候Buff还存在，则应该根据传入的skill_node种类延长对应的时间和层数'''
                pass
            # TODO:11111111111
            if skill_node.skill_trigger_buff_level == 2:
                pass
            else:
                self.max_duration = 1800
                self.max_count = 20

    def is_active(self, tick: int):
        """检查自身Buff状态是否存在"""
        if self.end_tick > tick:
            if self.count > 0:
                return True
        return False

    def end(self, tick: int):
        """Buff结束"""
        self.coordinated_support = False
        self.count = 0
        self.update_tick = tick


