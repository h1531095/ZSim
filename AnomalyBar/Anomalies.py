from dataclasses import dataclass
from AnomalyBar.AnomalyBarClass import AnomalyBar
import sys


@dataclass
class PhysicalAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()
        self.element_type = 0
        self.accompany_debuff = ['Buff-异常-畏缩']
        self.max_duration = 600

@dataclass
class FireAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        main_module = sys.modules['__main__']
        char_name_box = main_module.init_data.name_box
        self.accompany_dot = '灼烧'
        self.element_type = 1  # 火属性
        if '柏妮思' in char_name_box:
            self.max_duration = 600+180
        else:
            self.max_duration = 600

@dataclass
class IceAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        self.element_type = 2  # 冰属性
        self.accompany_debuff = ['Buff-异常-霜寒']
        self.accompany_dot = '冻结'
        self.max_duration = 600


@dataclass
class ElectricAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        main_module = sys.modules['__main__']
        char_name_box = main_module.init_data.name_box
        self.element_type = 3  # 电属性
        self.accompany_dot = '感电'
        if '丽娜' in char_name_box:
            self.max_duration = 600+180
        else:
            self.max_duration = 600



@dataclass
class EtherAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        self.element_type = 4  # 以太属性
        self.accompany_dot = '侵蚀'
        self.max_duration = 600


@dataclass
class FrostAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()  # 调用父类的初始化方法
        self.element_type = 5  # 烈霜属性（星见雅专属）
        self.accompany_dot = '冻结'
        self.accompany_debuff = ['Buff-异常-霜寒', 'Buff-角色-雅-核心被动-霜灼']
        self.max_duration = 600


# TODO：霜寒、霜灼作为一场绑定的debuff，有自己的退出机制，即新的异常发生了，那么老的buff要去掉。