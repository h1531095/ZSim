from Skill_Class import Skill


class Event:
    """
    事件类，初步设计：该类不包含Buff，目前只涉及动作，
    以后可能的拓展方向：后台协同攻击

    """
    def __init__(self):
        self.ft = self.EventFeature()
        self.dy = self.EventDynamic()

    class EventFeature:
        """
        记录了该事件的一些基本信息，比如事件的持续时间，事件的判定生效时间
        """
        def __init__(self):
            self.duration = 0
            self.judging_duration = 0

    class EventDynamic:
        def __init__(self, timenow):
            self.startticks = 0
            self.endticks = 0
            self.settlement_ticks = []  # 事件的结算节点，对于Skill来说，就是hit发生的ticks
            self.is_happening = False





