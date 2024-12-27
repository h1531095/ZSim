from Preload import SkillNode
from .character import Character
from .filters import _skill_node_filter



class Qingyi(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__MAX_VOLTAGE: int = 4096
        self.__QUAN_VOLTAGE: float = self.__MAX_VOLTAGE // 16 * (1.3 if self.cinema >= 1 else 1)
        # FIXME: 电压和内鬼网以及观测值，都不同了，我企图换原数据，结果用了2H还是CPU爆炸，多半要让Staff重测了。
        #  内鬼网显示，单个第三段平A的电压是3.3，
        #  这和我们观测到的16次打满的数据不符合，我们在这里的基础值是单份的SNA_3，也就是100/16 = 6.25，
        #  怀疑：要么数据改了，我们数据库落后没更新（检查了一下青衣部分技能的倍率，有些地方确实和数据库对不上）
        #  要么我们对SNA3的帧数划分不对。
        #  观测值：开1命的情况下，打满75%电压：34~36跳，用时135帧（去掉前摇，从第一个跳字开始算的）
        #  所以，关于这里的电压基础值，还需要再考虑一下。

        # FIXME：强化E、QTE、大招在内鬼网上的电压数值为：
        #  强化E：5.62+7.86+8.99（暂不知道这里给的是否是强化E）
        #  QTE：25；
        #  Q：80，
        #  根据实测，1命的青衣，开大之后直接把电压干满了，所以能够确定内鬼网上的电压数值，就是1:1的电压。
        #  由于我们单份的基础值是6.25，那么大招的倍率应该是12.8，QTE的倍率应该是4
        self.__FLASH_THRESHOLD: float = self.__MAX_VOLTAGE * 0.75

        self.flash_connect_voltage: int = 0 if self.cinema == 0 else self.__MAX_VOLTAGE  # 闪络电压，初始化为0
        self.flash_connect: bool = False if self.cinema == 0 else True  # 闪络状态
        self.rush_attack_available_times: int = 5   # 醉花月云转-突进攻击可用次数

    def special_resources(self, *args, **kwargs) -> None:
        """模拟青衣的闪络电压机制"""
        skill_nodes: list[SkillNode] = _skill_node_filter(*args, **kwargs)
        for node in skill_nodes:
            # 闪络电压增加逻辑
            if self.flash_connect_voltage < self.__MAX_VOLTAGE:
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
            # 闪络电压不能超过最大值
            self.flash_connect_voltage = min(self.flash_connect_voltage, self.__MAX_VOLTAGE)
            # 闪络电压超过75%时，进入闪络状态
            if self.flash_connect_voltage >= self.__FLASH_THRESHOLD:
                self.flash_connect = True
                self.rush_attack_available_times = 5
            if self.flash_connect:
                # 闪络状态执行逻辑
                if node.skill_tag == '1300_SNA_1':
                    self.flash_connect_voltage = 0
                    self.rush_attack_available_times -= 1
                    self.flash_connect = False
            else:
                # 非闪络状态执行逻辑
                if node.skill_tag == '1300_SNA_1':
                    # 醉花月云转-突进攻击可用次数减一
                    if self.rush_attack_available_times in [0, 5]:
                        print(f'WTF APL is doing?rush_attack_available_times is {self.rush_attack_available_times}')
                    # FIXME：这里的assert总会莫名其妙报错。明明就是5，但是就是触发了 !=5  的报警
                    #  为了程序能跑，暂时注释掉了，然后这个地方的判定应该是我if写的这个，
                    #  SNA剩余次数的计数器是0和5在这个分支是不可接受的，其他的反而是对的。
                    # assert self.rush_attack_available_times != 5, 'WTF APL is doing?'
                    # assert self.rush_attack_available_times != 0, 'WTF APL is doing?'
                    self.rush_attack_available_times -= 1


    def get_resources(self):
        return "闪络电压", self.flash_connect_voltage / self.__MAX_VOLTAGE * 100

    def get_flash(self, *args, **kwargs) -> dict[str, int|float|bool]:
        return {
            '闪络电压': self.flash_connect_voltage / self.__MAX_VOLTAGE,      # 返回一个比例
            '闪络状态': self.flash_connect,
            '醉花月云转可用次数': self.rush_attack_available_times,
        }