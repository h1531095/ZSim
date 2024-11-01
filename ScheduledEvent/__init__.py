import Preload
import Calcultor
import Enemy

class ScheduledData():
    def __init__(self):
        self.event_list = []

class ScheduledEvent:
    def __init__(self, tick, *events):
        for event in events:
            if event.preload_tick <= tick:
                self.event_start(event)

    @staticmethod
    def event_start(event):
        if isinstance(event, Preload.SkillNode):
            Calcultor.Caculator.cal_dmg_expect(event, Enemy)
