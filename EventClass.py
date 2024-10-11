from BuffClass import Buff
class Event:
    def __init__(self, timetick, buff:Buff=None):
        self.ft = self.EventFeature()
    class EventFeature:
        def __init__(self, name):
            self.eventindex = None  #独立ID
            self.eventfrom = name   #非独立ID
            self.starttime = 0
            self.endtime = 0
            self.duration = 0
            self.laststart = 0
            self.lastend = 0
   
    def Buffset(self, buff, timetick):
        """
        Buffset函数,在buff判定需要触发时调用.
        主要有以下几个功能:
        1,直接调用隔壁buff的几个判断函数,用来执行Buff触发时的一系列参数修改.
        比如:endtime的添加,starttime的添加,active状态的修改,甚至是dynamic buff list的修改.
        2,第1步会改变Buff的很多参数,在第一步完成后,将这些参数传给Event.EventFeature中的对应参数
        其中需要注意的是:eventindex的命名规则,以及eventfrom的命名规则
        3,


        """
        pass