from .Anomalies import PhysicalAnomaly, FireAnomaly, IceAnomaly, ElectricAnomaly, EtherAnomaly, FireIceAnomaly
from .AnomalyBarClass import AnomalyBar
from Disorder import Disorder

__all__ = [
    'AnomalyBar',
    'PhysicalAnomaly',
    'FireAnomaly',
    'IceAnomaly',
    'ElectricAnomaly',
    'EtherAnomaly',
    'FireIceAnomaly',
    'Disorder'
]

    # √TODO：属性异常应该拓展以下属性：①是否激活、②上一次激活时间、③、内置CD（虽然暂时没有改动的可能，但是要留好接口）④：已经处于异常状态的时间
    # √TODO：属性异常计算和快照累加的函数 ，
    # √TODO：改名 AnomalyBar
    # √TODO：5个异常条的派生类，以及随Enemy初始化的方法；
    # √TODO：Check myself 方法，检查自身是否属性异常

    # TODO：必须添加判断逻辑，判断当前的属性异常是否会覆盖老异常，亦或是会触发紊乱。（尽量自己和自己交互）
    # TODO：紊乱板块的计算，一旦发生紊乱（需要查询Enemy身上的异常池），需要立刻实例化一个“紊乱”对象抛出，
    # TODO：紊乱类的构建。

    # TODO：和Dot类的联动， 在触发属性异常时，创建dot，创建属性异常实例，传递快照并抛出实例，
    # TODO：重新构建Dot的结构，
