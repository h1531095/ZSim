from dataclasses import dataclass
import Enemy
import numpy as np

# TODO: __init__.py 只含有基类以及基类的方法与函数

#TODO: anomaly_snapshot.py 负责抄快照。需要内置一个快照累加的方法。异常伤害快照以 ndarray 形式储存，
# 顺序为：异常积蓄值，基础伤害区，增伤区，减易伤区，异常精通区，等级系数（只会传入角色等级）——该系数需要先加权平均等级，最后再换算成等级系数，因为涉及向下取整，异常增伤区，异常爆击区
# self.snpa_shot的2个索引，0:buildup  1:np.ndarray

#TODO: anomaly_dot.py 触发属性异常后，需要通过已经计算好的快照，生成一个Dot类实例，

element_type_list = ['PHY', 'FIRE', 'ICE', 'ELECTRIC', 'ETHER']


@dataclass
class AnomalyEffect:
    """
    这是属性异常类的基类。其中包含了属性异常的基本属性，以及几个基本方法。
    """
    enemy: Enemy
    element_type: int = None
    buildup: np.float64 = 0
    is_full: bool = False
    max_anomaly: float = None
    current_ndarray: np.ndarray = None
    current_anomaly: np.float64 = None
    anomaly_times: int = 0

    def __post_init__(self):
        # 从Enemy获取 max_anomaly的值
        self.max_anomaly = getattr(self.enemy, f'max_anomaly_{element_type_list[self.element_type]}', None)

    def update_max_anomaly(self):
        # 在触发属性异常后，更新对应属性的积蓄值，使其*1.02
        self.enemy.update_anomaly(self.element_type)

    def update_snap_shot(self, new_snap_shot: tuple):
        if new_snap_shot[0] not in [0, 1, 2, 3, 4]:
            raise TypeError(f'所传入的属性标号不正确！')
        if new_snap_shot[1] is not np.float64:
            raise TypeError(f'所传入的快照元组的第2个元素应该是np.float64！')
        if new_snap_shot[2] != (9, 1):
            raise TypeError(f'所传入的快照元组的第3个元素目前是{new_snap_shot[2].shape}的矩阵，但它应是一个9×1的矩阵！')
        ndarray = new_snap_shot[2]
        build_up_value = new_snap_shot[1]
        cal_result_1 = build_up_value * ndarray
        self.current_ndarray += cal_result_1
        self.current_ndarray += build_up_value
        if self.current_anomaly >= self.max_anomaly:
            self.anomaly_times += 1
            self.current_anomaly /= self.current_anomaly
            output = self.element_type, self.current_ndarray
            self.current_anomaly = np.float64(0)
            self.current_ndarray = np.zeros((9,1), dtype=np.float64)
            return output




