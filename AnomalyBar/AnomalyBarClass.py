from dataclasses import dataclass
import numpy as np
from Enemy import Enemy

# TODO: anomaly_dot.py 触发属性异常后，需要通过已经计算好的快照，生成一个Dot类实例，
# TODO: 属性异常的debuff效果以及dot效果


@dataclass
class AnomalyBar:
    """
    这是属性异常类的基类。其中包含了属性异常的基本属性，以及几个基本方法。
    """
    enemy: Enemy
    element_type: int = None  # 属性种类编号(1~5)
    is_full: bool = False  # 是否积满了
    current_ndarray: np.ndarray = None  # 当前快照总和
    current_anomaly: np.float64 = None  # 当前已经累计的积蓄值
    anomaly_times: int = 0  # 迄今为止触发过的异常次数
    active: bool = None    # 正处于属性异常状态下
    cd: int = None  # 属性异常的内置CD，
    last_active: int = None  # 上一次属性异常的时间

    def __post_init__(self):
        # 初始化时，自动重置current_ndarray以及current_anomaly，内置CD一般为3秒，所以是180
        self.current_ndarray = np.zeros((1, 1), dtype=np.float64)
        self.current_anomaly = np.float64(0)
        self.cd = 180
        self.active = False

    @property
    def max_anomaly(self):
        """
        每次访问 max_anomaly 时，从 enemy 实例动态获取最新的 max_anomaly 值。
        """
        # 获取 max_anomaly 的实际值，每次访问时都会更新
        element_type_list = ['PHY', 'FIRE', 'ICE', 'ELECTRIC', 'ETHER', 'FIREICE']
        return getattr(self.enemy, f'max_anomaly_{element_type_list[self.element_type]}', None)

    def get_current_snapshot(self):
        # 获取当前的快照和current_anomaly，供外部使用
        return self.current_ndarray, self.current_anomaly

    def update_max_anomaly(self):
        # 在触发属性异常后，更新对应属性的积蓄值，使其*1.02
        self.enemy.update_anomaly(self.element_type)

    def update_snap_shot(self, new_snap_shot: tuple):
        """
        该函数是更新快照的核心函数。但是并不具备识别属性种类的功能。
        所以需要在外部嵌套一个总函数，根据属性种类来执行不同属性的update函数。
        """
        if new_snap_shot[2] is not np.ndarray:
            raise TypeError(f'所传入的快照元组的第2个元素应该是np.ndarray！')
        new_ndarray = new_snap_shot[2]  # 获取新快照
        build_up_value = new_snap_shot[1]  # 获取积蓄值
        if self.current_ndarray.shape[0] != new_ndarray.shape[0]:
            # 扩展 current_ndarray 行数，保持已有数据，新增的部分会填充为零
            if self.current_ndarray.shape[0] < new_ndarray.shape[0]:
                # 扩展 current_ndarray 行数，增加零行
                new_shape = (new_ndarray.shape[0], 1)
                extended_ndarray = np.zeros(new_shape, dtype=np.float64)
                # 将已有的数据复制到新的 ndarray 中
                extended_ndarray[:self.current_ndarray.shape[0], :] = self.current_ndarray
                self.current_ndarray = extended_ndarray
            else:
                # 如果 current_ndarray 行数大于 new_ndarray 行数，直接裁剪 current_ndarray
                raise ValueError(f'传入的快照数组维度为{new_ndarray.shape[0]}，小于快照缓存的维度！')
        cal_result_1 = build_up_value * new_ndarray
        self.current_ndarray += cal_result_1
        self.current_anomaly += build_up_value

    def check_myself(self):
        # 仅用于检查自身是否积满的函数。不包含调用spawn_output的功能。
        if self.current_anomaly >= self.max_anomaly:
            self.is_full = True

    def spawn_output(self):
        """
        触发异常效果，重置数据并更新 max_anomaly。
        """
        self.anomaly_times += 1
        self.current_ndarray = self.current_ndarray / self.current_anomaly
        output = self.element_type, self.current_ndarray
        self.current_anomaly = np.float64(0)
        self.current_ndarray = np.zeros((1, self.current_ndarray.shape[0]), dtype=np.float64)  # 保持 1 列
        self.update_max_anomaly()
        return output
