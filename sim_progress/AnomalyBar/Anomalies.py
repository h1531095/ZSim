from dataclasses import dataclass
from sim_progress.AnomalyBar.AnomalyBarClass import AnomalyBar
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
        exist_buff_dict = main_module.load_data.exist_buff_dict
        self.element_type = 3  # 电属性
        self.accompany_dot = '感电'
        if '丽娜' in char_name_box:
            if "Buff-角色-丽娜-组队被动-延长感电" in exist_buff_dict['丽娜']:
                self.max_duration: int = 600 + 180
            else:
                self.max_duration: int = 600
        else:
            self.max_duration: int = 600


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
        self.accompany_debuff = ['Buff-异常-烈霜霜寒', 'Buff-角色-雅-核心被动-霜灼']
        self.max_duration = 1200
