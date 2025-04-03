import numpy as np
import pandas as pd
from sim_progress import AnomalyBar
from .EnemyAttack import EnemyAttackMethod
from sim_progress.Report import report_to_log
from sim_progress.data_struct import SingleHit
from define import ENEMY_DATA_PATH
from .QTEManager import QTEManager


class EnemySettings:
    def __init__(self):
        self.enemy_info_overwrite = False  # 是否强制覆盖怪物数据
        self.forced_no_stun = False
        self.forced_no_anomaly = False
        self.forced_stun_DMG_take_ratio: float = 1.5
        self.forced_anomaly: int = 0


class Enemy:
    def __init__(self, 
                 *, 
                 enemy_name: str | None = None, 
                 enemy_index_ID: int | None = None, 
                 enemy_sub_ID: int | None = None
                 ):
        """
        根据数据库信息创建怪物属性对象。

        三选一参数:（你不填也行，默认创建尼尼微作为木桩怪，因为她全部0抗性）
        - enemy_name (str): 敌人的中文名称
        - enemy_index_ID (int): 敌人的索引ID
        - enemy_sub_ID (int): 敌人的子ID，格式为9000+索引ID

        !!!注意!!!因为可能存在重名敌人的问题，使用中文名称查找怪物时，只会查找ID最靠前的那一个

        更新参数接口：
            hit_received(single_hit)
            update_stun(float)
        获取临时参数接口：
            get_hp_percentage()
            get_stun_percentage()
        """
        # 读取敌人数据文件，初始化敌人信息
        self.__last_stun_increase_tick: int | None = None
        _raw_enemy_dataframe = pd.read_csv(ENEMY_DATA_PATH)
        # !!!注意!!!因为可能存在重名敌人的问题，使用中文名称查找怪物时，只会返回ID更靠前的
        enemy_info = self.__lookup_enemy(_raw_enemy_dataframe, enemy_name, enemy_index_ID, enemy_sub_ID)
        self.name, self.index_ID, self.sub_ID, self.data_dict = enemy_info
        # 初始化动态属性
        self.dynamic = self.EnemyDynamic()
        # 初始化敌人基础属性
        self.max_HP: float = float(self.data_dict['剧变节点7理论生命值'])
        self.max_ATK: float = float(self.data_dict['剧变节点7攻击力'])
        self.max_stun: float = float(self.data_dict['剧变节点7失衡值上限'])
        self.max_DEF: float = float(self.data_dict['60级及以上防御力'])
        self.CRIT_damage: float = float(self.data_dict['暴击伤害'])
        self.able_to_be_stunned: bool = bool(self.data_dict['能否失衡'])
        self.able_to_get_anomaly: bool = bool(self.data_dict['能否异常'])
        self.stun_recovery_rate: float = float(self.data_dict['失衡恢复速度']) / 60
        self.stun_recovery_time: float = 0.0
        self.qte_manager = None
        self.stun_DMG_take_ratio: float = float(self.data_dict['失衡易伤值'])
        self.QTE_triggerable_times: int = int(self.data_dict['可连携次数'])
        # 初始化敌人异常状态抗性
        max_element_anomaly, self.max_anomaly_PHY = self.__init_enemy_anomaly(self.able_to_get_anomaly,
                                                                              self.QTE_triggerable_times)

        self.max_anomaly_ICE = self.max_anomaly_FIRE = self.max_anomaly_ETHER = self.max_anomaly_ELECTRIC = self.max_anomaly_FIREICE = max_element_anomaly

        # 初始化敌人其他防御属性
        self.interruption_resistance_level: int = int(self.data_dict['抗打断等级'])
        self.freeze_resistance: float = float(self.data_dict['冻结抵抗'])
        self.ICE_damage_resistance: float = float(self.data_dict['冰抗'])
        self.FIRE_damage_resistance: float = float(self.data_dict['火抗'])
        self.ELECTRIC_damage_resistance: float = float(self.data_dict['电抗'])
        self.ETHER_damage_resistance: float = float(self.data_dict['以太抗'])
        self.PHY_damage_resistance: float = float(self.data_dict['物抗'])

        # 初始化敌人设置
        self.settings = EnemySettings()
        self.__apply_settings(self.settings)

        # 下面的两个dict本来写在外面的，但是别的程序也要用这两个dict，所以索性写进来了。我是天才。
        self.trans_element_number_to_str = {0: 'PHY', 1: 'FIRE', 2: 'ICE', 3: 'ELECTRIC', 4: 'ETHER', 5: 'FIREICE'}
        self.trans_anomaly_effect_to_str = {0: 'assault', 1: 'burn', 2: 'frostbite', 3: 'shock', 4: 'corruption', 5: 'frost_frostbite'}
        """
        enemy实例化的时候，6种异常积蓄条也随着一起实例化。
        """

        self.fireice_anomaly_bar = AnomalyBar.FrostAnomaly()
        self.ice_anomaly_bar = AnomalyBar.IceAnomaly()
        self.fire_anomaly_bar = AnomalyBar.FireAnomaly()
        self.physical_anomaly_bar = AnomalyBar.PhysicalAnomaly()
        self.ether_anomaly_bar = AnomalyBar.EtherAnomaly()
        self.electric_anomaly_bar = AnomalyBar.ElectricAnomaly()
        """
        由于在AnomalyBar的init中有一个update_anomaly函数，
        该函数可以根据传入new_snap_shot: tuple 的第0位的属性标号，
        找到对应的anomaly_bar的实例，并且执行它的update_snap_shot 函数。
        以更新对应的积蓄快照。
        本来，这个dict应该建立在update_anomaly函数中，但是考虑到该函数会反复调用，频繁地创建这个dict会导致性能的浪费。
        所以将其挪到Enemy的init中，这样，这个dict只在Enemy实例化时被创建一次，
        然后update_anomaly函数将通过enemy.anomaly_bars_dict来调出对应的anomaly_bars实例。
        """
        self.anomaly_bars_dict: dict[int, AnomalyBar.AnomalyBar] = {
            0: self.physical_anomaly_bar,
            1: self.fire_anomaly_bar,
            2: self.ice_anomaly_bar,
            3: self.electric_anomaly_bar,
            4: self.ether_anomaly_bar,
            5: self.fireice_anomaly_bar,
        }
        # 在初始化阶段更新属性异常条最大值。
        for element_type in self.anomaly_bars_dict:
            anomaly_bar = self.anomaly_bars_dict[element_type]
            max_value = getattr(self, f'max_anomaly_{self.trans_element_number_to_str[element_type]}')
            anomaly_bar.max_anomaly = max_value

        if self.data_dict['进攻策略'] is None or self.data_dict['进攻策略'] is np.nan:
            attack_method_code = 0
        else:
            attack_method_code = int(self.data_dict['进攻策略'])
        self.attack_method = EnemyAttackMethod(attack_method_code)
        self.restore_stun()

        report_to_log(f'[ENEMY]: 怪物对象 {self.name} 已创建，怪物ID {self.index_ID}', level=4)

    def __restore_stun_recovery_time(self):
        self.stun_recovery_time = float(self.data_dict['失衡恢复时间']) * 60

    def restore_stun(self):
        """还原 Enemy 本身的失衡恢复时间，与QTE计数"""
        self.dynamic.stun = False
        self.dynamic.stun_bar = 0
        self.dynamic.stun_tick = 0
        self.__restore_stun_recovery_time()
        if self.qte_manager is None:
            self.qte_manager = QTEManager(self)
        self.qte_manager.qte_data.restore()

    def increase_stun_recovery_time(self, increase_tick: int):
        """更新失衡延长的时间，负责接收 Calculator 的 buff"""
        if self.__last_stun_increase_tick is None:
            self.__last_stun_increase_tick = increase_tick
        else:
            if increase_tick >= self.__last_stun_increase_tick:
                self.__last_stun_increase_tick = increase_tick
                self.__restore_stun_recovery_time()
                self.stun_recovery_time += increase_tick


    @staticmethod
    def __lookup_enemy(enemy_data: pd.DataFrame,
                       enemy_name: str | None = None,
                       enemy_index_ID: int | None = None,
                       enemy_sub_ID: int | None = None) -> tuple[str, int, int, dict]:
        """
        根据敌人名称或ID查找敌人信息，并返回敌人名称、IndexID和SubID。

        若输入多个参数，此函数会检测这些参数是否一一对应
        !!!注意!!!因为可能存在重名敌人的问题，使用中文名称查找怪物时，只会返回ID更靠前的
        因此，在已经输入了ID的情况下，函数不会优先根据中文名查找

        参数:
        - enemy_data: pd.DataFrame, 敌人数据 DataFrame，包含敌人信息。
        - enemy_name: str, 可选，敌人名称。
        - enemy_index_ID: int, 可选，敌人IndexID。
        - enemy_sub_ID: int, 可选，敌人SubID。
        """
        if enemy_index_ID is not None:
            row = enemy_data[enemy_data["IndexID"] == enemy_index_ID].to_dict('records')
        elif enemy_sub_ID is not None:
            row = enemy_data[enemy_data["SubID"] == enemy_sub_ID].to_dict('records')
        elif enemy_name is not None:
            row = enemy_data[enemy_data["CN_enemy_ID"] == enemy_name].to_dict('records')
        else:
            row = enemy_data[enemy_data["IndexID"] == 11531].to_dict('records')  # 默认打尼尼微（因为全部0抗）

        row_0: dict = row[0]
        name: str = row_0['CN_enemy_ID']
        index_ID: int = int(row_0['IndexID'])
        sub_ID: int = int(row_0['SubID'])

        # 检查输入的变量与查到的变量是否一致
        if enemy_name is not None:
            if name != enemy_name:
                raise ValueError("传入的name与ID不匹配")
        if enemy_index_ID is not None:
            if index_ID != enemy_index_ID:
                raise ValueError("传入的name与ID不匹配")
        if enemy_sub_ID is not None:
            if sub_ID != enemy_sub_ID:
                raise ValueError("传入的name与ID不匹配")

        return name, index_ID, sub_ID, row_0

    @staticmethod
    def __init_enemy_anomaly(able_to_get_anomaly: bool, QTE_triggerable_times: int) -> tuple[int | float, int | float]:
        """
        根据敌人的异常能力和QTE触发次数(怪物等阶)初始化敌人的异常值。

        参数:
        able_to_get_anomaly (bool): 敌人是否能获得异常值。
        QTE_triggerable_times (int): QTE可触发的次数。

        返回:
        tuple: 包含两个值，分别为基础异常值和物理异常值。
        """
        if able_to_get_anomaly:
            # 定义基础异常值
            base_anomaly = 150
            # 定义物理异常值的乘数
            physical_anomaly_mul = 1.2
            # 计算物理异常值
            base_anomaly_physical = base_anomaly * physical_anomaly_mul
            # 根据QTE触发次数返回相应的异常值
            if QTE_triggerable_times == 1:
                return base_anomaly * 4, base_anomaly_physical * 4
            elif QTE_triggerable_times == 2:
                return base_anomaly * 15, base_anomaly_physical * 15
            elif QTE_triggerable_times == 3:
                return base_anomaly * 20, base_anomaly_physical * 20
            else:
                # 如果QTE触发次数不符合已定义的条件，返回默认异常值
                return 3000, 3600  # 默认异常值
        else:
            return 0, 0

    def __apply_settings(self, settings: EnemySettings):
        if settings.enemy_info_overwrite:
            if settings.forced_no_stun:
                self.able_to_be_stunned = False
            if settings.forced_no_anomaly:
                self.able_to_get_anomaly = False
            self.stun_DMG_take_ratio = settings.forced_stun_DMG_take_ratio
        else:
            pass

    def __qte_tag_filter(self, tag: str) -> list[str]:
        """判断输入的标签是否为QTE，并作为列表返回"""
        result = []
        if 'QTE' in tag:
            result.append(tag)
        return result

    def update_anomaly(self, element: str | int = "ALL", *, times: int = 1) -> None:
        """更新怪物异常值，触发一次异常后调用。"""
        # 检查参数类型
        if not isinstance(element, (str, int)) :
            raise TypeError(f"element参数类型错误，必须是整数或字符串，实际类型为{type(element)}")
        if not isinstance(times, int):
            raise TypeError(f"times参数必须是整数，实际类型为{type(times)}")
        if times <= 0:
            raise ValueError(f"times参数必须大于0，实际值为{times}")

        update_ratio = 1.02
        '''游戏中，每次异常增加2%对应属性异常值'''

        try:
            assert isinstance(element, str)
            element = element.upper()
        except AssertionError:
            pass

        for _ in range(int(np.floor(times))):
            if element == 'ICE' or element == '冰' or element == 2:
                self.max_anomaly_ICE *= update_ratio
            elif element == 'FIRE' or element == '火' or element == 1:
                self.max_anomaly_FIRE *= update_ratio
            elif element == 'ETHER' or element == '以太' or element == 4:
                self.max_anomaly_ETHER *= update_ratio
            elif element == 'ELECTRIC' or element == '电' or element == 3:
                self.max_anomaly_ELECTRIC *= update_ratio
            elif element == 'PHY' or element == '物理' or element == 0:
                self.max_anomaly_PHY *= update_ratio
            elif element == 'FIREICE' or element == '烈霜' or element == 5:
                self.max_anomaly_FIREICE *= update_ratio
            elif isinstance(element, str) and ('ALL' in element or '全部' in element or '所有' in element):
                self.max_anomaly_ICE *= update_ratio
                self.max_anomaly_FIRE *= update_ratio
                self.max_anomaly_ETHER *= update_ratio
                self.max_anomaly_ELECTRIC *= update_ratio
                self.max_anomaly_PHY *= update_ratio
                self.max_anomaly_FIREICE *= update_ratio
            else:
                raise ValueError(f"输入了不支持的元素种类：{element}")

    def update_stun(self, stun: np.float64) -> None:
        self.dynamic.stun_bar += stun

    def hit_received(self, single_hit: SingleHit, tick: int) -> None:
        """实现怪物的QTE次数计算、扣血计算等受击时的对象结算，与伤害计算器对接"""
        """
        在20250325的更新中，更新了receive_hit中处理数据的顺序。并且在receive_hit中增加了重复的stun_judge。
        进行这一更新的原因有些复杂，详细描述如下：
        原有逻辑：在preload的第一个步骤：自检阶段 进行失衡检查（即运行enemy.stun_judge()）——这也是整个程序中唯一进行stun_judge的地方，这样起码可以保证每个tick执行一次。
        导致问题：如果一个tick中含有多个Hit，且其中某个hit打满了失衡值，且当前后续的hit中含有重攻击，错误的数据更新顺序就会让QTE管理器失效，
        从而影响到下个Tick的APL的判断，使其输出错误动作：比如QTE后置，甚至整个失衡阶段被完全跳过。
        以实际发现的问题为例：
            上一个动作为重攻击，且最后一个hit恰好打满了失衡条，那么就会导致一个顺序错误：
            在第n tick:
                receive_hit中的qte_manager先执行，然后再更新stun_bar，然后在下个tick更新stun状态
                qte_manager虽然成功接收到了足以激发连携的重攻击，但是此时无论是stun_bar还是stun状态都不足以让连携成功激发
            在第n+1 tick:
                preload的自检阶段，stun_judge执行，确实将stun状态更改为True，但是本应该在上个hit因为重攻击而激发的连携技，却错过了窗口，
            导致：
                连携技只能等待下一个重攻击才能被激发了——这种情况会严重误导APL的判断，让它一直认为：怪物正处于彩色失衡、且连携技尚未激发的状态，
            如果我针对这一状态设置的APL策略为 "等待"：
                [APL Code]: 0000|action+=|wait|status.enemy:stun==True|status.enemy.status.enemy:QTE_activation_available==True|status.enemy:single_qte==None
            那么角色就会一直等待下去，一直到enemy.stun为False——具体表现为整个连携技阶段被完全跳过。
        最终解决方案：只有让qte_manager最后一个执行，并且stun_judge必须在stun_bar更新后立刻执行，才能够让连携技成功激发。
        显然，这会导致一个tick中多次执行stun_judge，会导致一部分的性能开销，但是实际影响估计很小，影响不大。
        """
        # 更新失衡，为减少函数调用
        self.dynamic.stun_bar += single_hit.stun
        self.stun_judge(tick)
        # 怪物的扣血逻辑。
        self.__HP_update(single_hit.dmg_expect)

        # 更新异常值
        self.__anomaly_prod(single_hit.snapshot)
        # 更新连携管理器
        self.qte_manager.receive_hit(single_hit)

        # 遥远的需求：
    # TODO：实时DPS的计算，以及预估战斗结束时间，用于进一步优化APL。（例：若目标预计死亡时间<5秒，则不补buff）

    def get_hp_percentage(self) -> float:
        """获取当前生命值百分比的方法"""
        return 1 - self.dynamic.lost_hp / self.max_HP

    def get_stun_percentage(self) -> float:
        """获取当前失衡值百分比的方法"""
        return self.dynamic.stun_bar / self.max_stun

    def stun_judge(self, _tick: int) -> bool:
        """判断敌人是否处于 失衡 状态，并更新 失衡 状态"""
        if not self.able_to_be_stunned:
            self.dynamic.stun_update_tick = _tick
            return False

        if self.dynamic.stun:
            # 如果已经是失衡状态，则判断是否恢复
            if self.stun_recovery_time <= self.dynamic.stun_tick:
                self.dynamic.stun_update_tick = _tick
                self.restore_stun()
            else:
                if _tick - self.dynamic.stun_update_tick > 1:
                    raise ValueError(f'状态更新间隔大于1！存在多个tick都未更新stun的情况！')
                self.dynamic.stun_update_tick = _tick
                self.dynamic.stun_tick += 1
        else:
            if self.dynamic.stun_bar >= self.max_stun:
                # 若是检测到失衡状态的上升沿，则应该开启彩色失衡状态。
                self.qte_manager.qte_data.reset()
                print(f'怪物陷入失衡了！')
                self.dynamic.stun = True
                self.dynamic.stun_update_tick = _tick
        return self.dynamic.stun

    def __HP_update(self, dmg_expect: np.float64) -> None:
        self.dynamic.lost_hp += dmg_expect
        if (minus := self.max_HP - self.dynamic.lost_hp) <= 0:
            self.dynamic.lost_hp = -1 * minus
            report_to_log(f'怪物{self.name}死亡！')

    def __anomaly_prod(self, snapshot: tuple[int, np.float64, np.ndarray]) -> None:
        if snapshot[1] >= 1e-6: # 确保非零异常值才更新
            element_type_code = snapshot[0]
            updated_bar = self.anomaly_bars_dict[element_type_code]
            updated_bar.update_snap_shot(snapshot)

    class EnemyDynamic:
        def __init__(self):
            self.stun = False  # 失衡状态
            self.stun_update_tick = 0   # 上次更新失衡状态的时间
            self.frozen = False  # 冻结状态
            self.frostbite = False  # 霜寒状态
            self.frost_frostbite = False  # 烈霜霜寒状态
            self.assault = False  # 畏缩状态
            self.shock = False  # 感电状态
            self.burn = False  # 灼烧状态
            self.corruption = False  # 侵蚀状态

            self.dynamic_debuff_list = []   # 用来装debuff的list
            self.dynamic_dot_list = []      # 用来装dot的list
            self.active_anomaly_bar_dict = {number: None for number in range(6)}    # 用来装激活属性异常的字典。

            self.stun_bar = 0   # 累计失衡条
            self.lost_hp = 0    # 已损生命值
            self.stun_tick = 0  # 失衡已进行时间

            self.frozen_tick = 0
            self.frostbite_tick = 0
            self.assault_tick = 0
            self.shock_tick = 0
            self.burn_tick = 0
            self.corruption_tick = 0

        def __str__(self):
            return f"失衡: {self.stun}, 失衡条: {self.stun_bar:.2f}, 冻结: {self.frozen}, 霜寒: {self.frostbite}, 畏缩: {self.assault}, 感电: {self.shock}, 灼烧: {self.burn}, 侵蚀：{self.corruption}, 烈霜霜寒：{self.frost_frostbite}"

    def __str__(self):
        return f"{self.name}: {self.dynamic.__str__()}"



if __name__ == '__main__':
    test = Enemy(enemy_index_ID=11432, enemy_sub_ID=900011432)
    print(test.ice_anomaly_bar.max_anomaly)


