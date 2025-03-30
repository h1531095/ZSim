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

    def after_shock_happend(self, tick: int):
        """抛出aftershock的skill_tag，并且更新自身信息"""
        self.update_tick = tick
        return self.active_result


class AfterShockManager:
    """协同攻击管理器， 服务于角色——扳机"""
    def __init__(self):
        self.normal_after_shock = AfterShock('1361_CoAttack_A', 180)
        self.strong_after_shock = AfterShock('1361_CoAttack_1', 300)
        self.free_after_shock = AfterShock('1361_CoAttack_A', 0)
        self.coordinated_support_manager = None
        self.char = None

    def spawn_after_shock(self, tick: int, skill_node) -> str | None:
        """根据传入的skill_node抛出对应的协同攻击，并且更新自身数据；"""
        if self.char is None:
            from sim_progress.Buff import JudgeTools
            self.char = JudgeTools.find_char_from_CID(1361)
        if not self.char.is_available(tick):
            return None
        if skill_node.skill.trigger_buff_level in [2, 6, 9]:
            '''优先判断强协同攻击'''
            if self.strong_after_shock.is_ready(tick):
                if self.char.get_resource()[1] >= 5:
                    return self.strong_after_shock.after_shock_happend(tick)
        if self.coordinated_support_manager.active:
            pass
        else:
            if skill_node.skill_trigger_buff_level in [0, 1, 3, 4, 7]:
                '''普通协同'''
                pass
            elif skill_node.skill_trigger_buff_level in [2, 6, 9]:
                '''强化强协同'''
                pass
            else:
                return None




