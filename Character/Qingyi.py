from Preload import SkillNode
from .character import Character
from .filters import _skill_node_filter


class Qingyi(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__MAX_VOLTAGE: int = 4096
        self.__QUAN_VOLTAGE: float = self.__MAX_VOLTAGE // 16 * (1.3 if self.cinema >= 1 else 1)
        self.__FLASH_THRESHOLD: float = self.__MAX_VOLTAGE * 0.75

        self.flash_connect_voltage: int = 0 if self.cinema == 0 else self.__MAX_VOLTAGE  # 闪络电压，初始化为0
        self.flash_connect: bool = False if self.cinema == 0 else True  # 闪络状态
        self.rush_attack_available_times: int = 5   # 醉花月云转-突进攻击可用次数

    def special_resources(self, *args, **kwargs) -> None:
        """模拟青衣的闪络电压机制"""
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            if self.flash_connect:
                # 闪络状态执行逻辑
                if node.skill_tag == '1300_SNA_1':
                    self.flash_connect_voltage = 0
                    self.rush_attack_available_times -= 1
                    self.flash_connect = False
            else:
                # 非闪络状态执行逻辑
                if node.skill_tag == '1300_NA_3_NFC':
                    self.flash_connect_voltage += self.__QUAN_VOLTAGE
                elif node.skill_tag == '1300_NA_3_FC':
                    self.flash_connect_voltage = self.__MAX_VOLTAGE
                elif node.skill_tag == '1300_E':
                    self.flash_connect_voltage += self.__QUAN_VOLTAGE * 2
                elif node.skill_tag == '1300_E_EX_NFC':
                    self.flash_connect_voltage += self.__QUAN_VOLTAGE * 4
                elif node.skill_tag == '1300_E_EX_FC':
                    self.flash_connect_voltage += self.__QUAN_VOLTAGE * 6
                elif node.skill_tag == '1300_QTE':
                    self.flash_connect_voltage += self.__QUAN_VOLTAGE * 8
                elif node.skill_tag == '1300_Q':
                    self.flash_connect_voltage += self.__QUAN_VOLTAGE * 12
                elif node.skill_tag == '1300_SNA_1':
                    # 醉花月云转-突进攻击可用次数减一
                    assert self.rush_attack_available_times != 5, 'WTF APL is doing?'
                    assert self.rush_attack_available_times != 0, 'WTF APL is doing?'
                    self.rush_attack_available_times -= 1
                # 闪络电压超过75%时，进入闪络状态
                if self.flash_connect_voltage > self.__FLASH_THRESHOLD:
                    self.flash_connect = True
                    self.rush_attack_available_times = 5
                # 闪络电压不能超过最大值
                self.flash_connect_voltage = min(self.flash_connect_voltage, self.__MAX_VOLTAGE)

    def get_resources(self, *args, **kwargs) -> dict[str, int|float|bool]:
        return {
            '闪络电压': self.flash_connect_voltage / self.__MAX_VOLTAGE,      # 返回一个比例
            '闪络状态': self.flash_connect,
            '醉花月云转可用次数': self.rush_attack_available_times,
        }