class Buff:
    def __init__(self, config):
        self.info = self.Buff_Infomation(config)
        self.logic = self.Buff_Logic(config)
        self.effect
        self.update_logic = config['update_logic']
    class Buff_Infomation:
        def __init__(self, config):
            self.name = config['name']
            self.durationtype = config['durationtype']
            self.maxduration = config['maxduration']
            self.maxcount = config['maxcount']
            self.active = False
            self.duration = 0
            self.count = 0
    class Buff_Logic():
        def __init__(self, config):
            self.logic = config['logic']
    class Buff_Effect():
        def __init__(self):
            pass
    def end(self):
        self.info.duration = 0
        self.info.active = False
        self.info.count = 0
    def update(self, timecost, step):
        self.duration = min(self.duration - timecost, 0)
        self.count = min(self.info.count + step, self.info.maxcount)
        if self.info.count == 0 or self.info.duration == 0:
            self.end()
