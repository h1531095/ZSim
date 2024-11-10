from dataclasses import dataclass
from AnomalyBar.AnomalyBarClass import AnomalyBar


@dataclass
class PhysicalAnomaly(AnomalyBar):
    def __post_init__(self):
        self.element_type = 0
        super().__post_init__()


@dataclass
class FireAnomaly(AnomalyBar):
    def __post_init__(self):
        self.element_type = 1  # 火属性
        super().__post_init__()  # 调用父类的初始化方法


@dataclass
class IceAnomaly(AnomalyBar):
    def __post_init__(self):
        self.element_type = 2  # 冰属性
        super().__post_init__()  # 调用父类的初始化方法


@dataclass
class ElectricAnomaly(AnomalyBar):
    def __post_init__(self):
        self.element_type = 3  # 电属性
        super().__post_init__()  # 调用父类的初始化方法


@dataclass
class EtherAnomaly(AnomalyBar):
    def __post_init__(self):
        self.element_type = 4  # 以太属性
        super().__post_init__()  # 调用父类的初始化方法


@dataclass
class FireIceAnomaly(AnomalyBar):
    def __post_init__(self):
        self.element_type = 5  # 烈霜属性（星见雅专属）
        super().__post_init__()  # 调用父类的初始化方法
