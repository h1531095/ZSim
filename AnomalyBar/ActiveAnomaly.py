from .AnomalyBarClass import AnomalyBar
import numpy as np


def spawn_output(anomaly_bar):
    if not isinstance(anomaly_bar, AnomalyBar):
        raise TypeError(f'{anomaly_bar}不是AnomalyBar类！')
    """
    触发异常效果，重置数据并更新 max_anomaly。
    """
    anomaly_bar.anomaly_times += 1
    anomaly_bar.current_ndarray = anomaly_bar.current_ndarray / anomaly_bar.current_anomaly
    output = anomaly_bar.element_type, anomaly_bar.current_ndarray
    anomaly_bar.current_anomaly = np.float64(0)
    anomaly_bar.current_ndarray = np.zeros((1, anomaly_bar.current_ndarray.shape[0]), dtype=np.float64)  # 保持 1 列
    return output


def ActiveAnomaly(bar_dict: dict, element_type: int):
    bar = bar_dict[element_type]
    if not isinstance(bar, AnomalyBar):
        raise TypeError(f'{bar}不是Anomaly类！')
    output = spawn_output(bar)
    pass