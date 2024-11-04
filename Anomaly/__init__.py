from dataclasses import dataclass
import Enemy
# TODO: __init__.py 负责两个文件的交流。

#TODO: anomaly_snapshot.py 负责抄快照。需要内置一个快照累加的方法。异常伤害快照以 ndarray 形式储存，
# 顺序为：异常积蓄值，基础伤害区，增伤区，减易伤区，异常精通区，等级系数（只会传入角色等级）——该系数需要先加权平均等级，最后再换算成等级系数，因为涉及向下取整，异常增伤区，异常爆击区

#TODO: anomaly_dot.py 触发属性异常后，需要通过已经计算好的快照，生成一个Dot类实例，

@dataclass
class AnomalyEffect:
    """
    这是属性异常类的基类。其中包含了属性异常的基本属性，以及几个基本方法。
    """
    enemy: Enemy
    element_type: int = None
    buildup: int = 0
    is_full: bool = False
    max_anomaly: float = None

    def __post_init__(self):
        # 从Enemy获取 max_anomaly的值
        pass



