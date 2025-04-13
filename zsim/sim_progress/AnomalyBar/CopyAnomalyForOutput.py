from sim_progress.AnomalyBar.AnomalyBarClass import AnomalyBar


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


class PolarityDisorder(AnomalyBar):
    """
    柳的极性紊乱（不含核心被动的紊乱基础倍率增加）
    极性紊乱的计算公式为：
    极性紊乱伤害 = 紊乱伤害 * 本次极性紊乱倍率（解锁2命后可变）+ 附加3200% * 精通的伤害
    构造时，不仅需要提供被复制的异常条，还需要提供连击次数（用来计算极性紊乱比例），还需要提供触发者ID（CID或者enemy）
    """

    def __init__(self, Output_bar: AnomalyBar, _polarity_disorder_ratio: float, active_from: int | str):
        super().__init__()
        self.__dict__.update(Output_bar.__dict__)
        if not any([active_from == 'enemy',
                    isinstance(active_from, int) and len(str(active_from)) == 4]):
            raise ValueError("极性紊乱的触发者ID必须是角色的CID或者enemy")
        self.is_disorder = True
        self.polarity_disorder_ratio = _polarity_disorder_ratio  # 极性紊乱对比紊乱的缩放比例
        self.active_from = active_from      # 极性紊乱的触发者ID

