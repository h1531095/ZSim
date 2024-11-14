from .Anomalies import PhysicalAnomaly, FireAnomaly, IceAnomaly, ElectricAnomaly, EtherAnomaly, FireIceAnomaly
from .AnomalyBarClass import AnomalyBar
from .CopyAnomalyForOutput import Disorder

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

    # TODO：和Dot类的联动， 在触发属性异常时，创建dot，创建属性异常实例，传递快照并抛出实例，
    # TODO：重新构建Dot的结构，
