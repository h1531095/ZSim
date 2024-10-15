from TickClass import TIMETICK
import math


class Event:
    """
    事件类，初步设计：该类不包含Buff，目前只涉及动作，
    以后可能的拓展方向：后台协同攻击

    """
    def __init__(self, start_ticks, end_ticks, settelment_count):
        self.dy = self.EventDynamic(start_ticks, end_ticks, settelment_count)

    class EventDynamic:
        def __init__(self, start_ticks, end_ticks, settelment_count):
            self.start_ticks = start_ticks
            self.end_ticks = end_ticks
            self.settlement_ticks = []  # 事件的结算节点，对于Skill来说，就是hit发生的ticks
            step = (end_ticks - start_ticks) / settelment_count
            for i in range(settelment_count):
                self.settlement_ticks.append(start_ticks + (i + 1) * step)

    def is_happening(self):
        if TIMETICK in range(self.dy.start_ticks, self.dy.end_ticks):
            return True
        else:
            return False

    def check_current_event(self):
        if TIMETICK == self.dy.start_ticks:
            return "start"
        elif TIMETICK == self.dy.end_ticks:
            return "end"
        elif TIMETICK == math.ceil(self.dy.settlement_ticks[0]):
            return "settlement"




