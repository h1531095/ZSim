import sys

from Preload import SkillNode
from Report import report_to_log
from .character import Character
from .filters import _skill_node_filter


class Qingyi(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.MAX_VOLTAGE: int = 4096
        self.QUAN_VOLTAGE: int = self.MAX_VOLTAGE // 16
        self.flash_connect_voltage: int = 0 if self.cinema == 0 else self.MAX_VOLTAGE  # 闪络电压，初始化为0
        self.flash_connect: bool = False if self.cinema == 0 else True

    def special_resources(self, *args, **kwargs) -> None:
        """模拟青衣的闪络电压机制"""
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            if self.flash_connect:
                if node.skill_tag == '1300_SNA_1':
                    self.flash_connect_voltage = 0
            else:
                if node.skill_tag == '1300_NA_3_NFC':
                    self.flash_connect_voltage += self.QUAN_VOLTAGE
                    if self.flash_connect_voltage <= self.MAX_VOLTAGE * 0.75:
                        pass
                    else:
                        self.flash_connect = True
                elif node.skill_tag == '1300_NA_3_FC':
                    self.flash_connect_voltage = self.MAX_VOLTAGE
                    self.flash_connect = True
                elif node.skill_tag == '1300_SNA_1':
                    log: str = f'{self.NAME}在非闪络状态使用了醉花月云转'
                    report_to_log(log)
                    print(log)
                self.flash_connect_voltage = min(self.flash_connect_voltage, self.MAX_VOLTAGE)

    def get_resources(self, *args, **kwargs) -> dict[str, int|float]:
        return {
            '闪络电压': self.flash_connect_voltage / self.MAX_VOLTAGE,      # 返回一个比例
            '闪络状态': self.flash_connect,
        }