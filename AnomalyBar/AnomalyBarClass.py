from dataclasses import dataclass
import numpy as np


@dataclass
class AnomalyBar:
    """
    这是属性异常类的基类。其中包含了属性异常的基本属性，以及几个基本方法。
    """
    element_type: int = None  # 属性种类编号(1~5)
    is_disorder: bool = None # 是否是紊乱实例
    is_full: bool = False  # 是否积满了
    current_ndarray: np.ndarray = None  # 当前快照总和
    current_anomaly: np.float64 = None  # 当前已经累计的积蓄值
    anomaly_times: int = 0  # 迄今为止触发过的异常次数
    cd: int = None  # 属性异常的内置CD，
    last_active: int = None  # 上一次属性异常的时间
    max_anomaly: int = None  # 最大积蓄值
    ready: bool = None  # 内置CD状态
    accompany_debuff: bool = None   # 是否在激活时伴生debuff
    accompany_dot: bool = None  # 是否在激活时伴生dot

    def __post_init__(self):
        # 初始化时，自动重置current_ndarray以及current_anomaly，内置CD一般为3秒，所以是180
        self.current_ndarray = np.zeros((1, 1), dtype=np.float64)
        self.current_anomaly = np.float64(0)
        self.cd = 180
        self.is_disorder = False
        self.last_active = 0
        self.ready = True

    def update_snap_shot(self, new_snap_shot: tuple):
        """
        该函数是更新快照的核心函数。但是并不具备识别属性种类的功能。
        所以需要在外部嵌套一个总函数，根据属性种类来执行不同属性的update函数。
        """
        if not isinstance(new_snap_shot[2], np.ndarray):
            raise TypeError(f'所传入的快照元组的第3个元素应该是np.ndarray！')

        new_ndarray = new_snap_shot[2].reshape(1, -1)  # 将数据重塑为一行多列的形式
        build_up_value = new_snap_shot[1]  # 获取积蓄值

        if self.current_ndarray.shape[1] != new_ndarray.shape[1]:
            # 扩展 current_ndarray 列数，保持已有数据，新增的部分会填充为零
            if self.current_ndarray.shape[1] < new_ndarray.shape[1]:
                # 扩展 current_ndarray 列数，增加零列
                new_shape = (1, new_ndarray.shape[1])
                extended_ndarray = np.zeros(new_shape, dtype=np.float64)
                # 将已有的数据复制到新的 ndarray 中
                extended_ndarray[:, :self.current_ndarray.shape[1]] = self.current_ndarray
                self.current_ndarray = extended_ndarray
            else:
                # 如果 current_ndarray 列数大于 new_ndarray 列数，直接裁剪 current_ndarray
                raise ValueError(f'传入的快照数组列数为{new_ndarray.shape[1]}，小于快照缓存的列数！')

        cal_result_1 = build_up_value * new_ndarray

        self.current_ndarray += cal_result_1
        self.current_anomaly += build_up_value

    def ready_judge(self, timenow):
        if timenow - self.last_active >= self.cd:
            self.ready = True
