from AnomalyBar.AnomalyBarClass import AnomalyBar


class Disorder(AnomalyBar):
    """
    紊乱类，当这个类被创建，将会在__init__方法中自动调用__dict__方法，立刻复制父类的所有状态。
    注意，语法上，在创建Disorder实例时，需要在括号里传入需要复制的父类实例。
    Disorder会打开自身的is_disorder
    """
    def __init__(self, Output_bar: AnomalyBar):
        super().__init__()
        self.__dict__.update(Output_bar.__dict__)
        self.is_disorder = True
        # 复制父类的所有属性，主要是快照、积蓄总值、属性类型。



class NewAnomaly(AnomalyBar):
    """
    普通的异常类，仅用于非紊乱的属性异常更新。
    """

    def __init__(self, Output_bar: AnomalyBar):
        super().__init__()
        self.__dict__.update(Output_bar.__dict__)



