from sim_progress.Preload import SkillNode


class Shinrabanshou:
    def __init__(self, cinema: int):
        self.max_duration = 900 if cinema < 6 else 1800
        self.update_tick = 0

    def statement(self, tick: int):
        """查询 柳的森罗万象状态的方法"""
        if self.update_tick == 0:
            return False
        if tick - self.update_tick >= self.max_duration:
            return False
        return True

    def active(self):
        """更新森罗万象的时间！"""
        from sim_progress.Buff import find_tick
        tick = find_tick()
        self.update_tick = tick


class StanceManager:
    """柳的架势管理器"""
    def __init__(self, char_instance):
        self.char = char_instance
        self.stance_jougen = True      # 上弦状态，初始化时就是上弦
        self.stance_kagen = False       # 下弦状态
        self.last_update_node = None        # 上次导致更新的skill_node
        self.shinrabanshou = Shinrabanshou(self.char.cinema)        # 森罗万象管理器

    def update_myself(self, skill_node: SkillNode, tick):
        """接收skill_node，并且判断自身架势是否要改变；"""
        skill_tag = skill_node.skill_tag

        '''首先筛掉不是自己的skill_node'''
        if '1221' not in skill_tag:
            return

        '''若传入的skill_node不能触发任何架势直接返回！'''
        if skill_tag not in ['1221_E', '1221_E_A', '1221_QTE', '1221_Assault_Aid', '1221_E_EX_1']:
            return

        '''若检测到强化E 突刺攻击，则只放行首次突刺攻击，后续的突刺攻击完全不放行。'''
        if skill_tag == '1221_E_EX_1' and self.last_update_node.skill_tag == skill_tag:
            return

        self.last_update_node = skill_node
        self.change_stance()
        if skill_tag == '1221_E_EX_1':
            '''如果强化E的突刺攻击到了这个分支还在，则说明是第一次突刺攻击，则可以触发森罗万象。'''
            self.shinrabanshou.active(tick)

    def change_stance(self):
        """更新架势"""
        if self.stance_jougen == self.stance_kagen:
            raise ValueError('上弦、下弦状态不能同时为True或False！')
        if self.stance_jougen:
            self.stance_jougen = False
            self.stance_kagen = True
        else:
            self.stance_jougen = True
            self.stance_kagen = False

    @property
    def stance_now(self):
        """返回当前的架势状态，True是上弦，False是下弦"""
        if self.stance_jougen:
            return True
        elif self.stance_kagen:
            return False
        else:
            raise ValueError('上弦、下弦状态不能同时为True或False！')
