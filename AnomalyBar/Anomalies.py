from dataclasses import dataclass
from AnomalyBar.AnomalyBarClass import AnomalyBar


@dataclass
class PhysicalAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()
        self.element_type = 0
        self.accompany_debuff = '畏缩'


@dataclass
class FireAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        self.accompany_dot = '灼烧'
        self.element_type = 1  # 火属性


@dataclass
class IceAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        self.element_type = 2  # 冰属性
        self.accompany_debuff = '霜寒'
        self.accompany_dot = '冻结'


@dataclass
class ElectricAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        self.element_type = 3  # 电属性
        self.accompany_dot = '感电'



@dataclass
class EtherAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        self.element_type = 4  # 以太属性
        self.accompany_dot = '侵蚀'


@dataclass
class FireIceAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        self.element_type = 5  # 烈霜属性（星见雅专属）
        self.accompany_dot = '冻结'
        self.accompany_debuff = '霜寒'
