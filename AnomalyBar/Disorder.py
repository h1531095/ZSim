from AnomalyBar.AnomalyBarClass import AnomalyBar
import Enemy
from dataclasses import dataclass


@dataclass
class Disorder(AnomalyBar):
    """
    紊乱类，继承自AnomalyBar，只读取并保存当前快照和current_anomaly
    """
    def __post_init__(self):
        # 初始化时，读取当前的快照和积蓄值
        self.current_ndarray = self.enemy.current_ndarray.copy()
        self.current_anomaly = self.enemy.current_anomaly