class AfterShock:
    """协同攻击基类"""
    def __init__(self, skill_tag: str, cd: int):
        self.update_tick = 0
        self.cd = cd
        self.active_result = skill_tag

    def is_ready(self, tick: int):
        # TODO：先写一个临时的
        if tick - self.update_tick >= self.cd:
            return True
        return False


class AfterShockManager:
    """协同攻击管理器， 服务于角色——扳机"""
    def __init__(self):
        self.coordinated_support = False
        self.normal_after_shock = AfterShock('1361_CoAttack_A', 180)
        self.strong_after_shock = AfterShock('1361_CoAttack_1', 300)
        self.free_after_shock = AfterShock('1361_CoAttack_A', 0)


