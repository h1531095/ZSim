from Enemy import Enemy


def update_anomaly(enemy: Enemy, new_snap_shot: tuple):
    """
    该函数需要传入enemy以及new_snap_shot，当snpashot尺寸不对时会报错。
    它会根据snpa_shot中的属性标号，去enemy.anomaly_bars_dict中找出对应的异常条的实例，并且执行该实例的update_snap_shot函数。
    """
    if len(new_snap_shot) != 3:
        raise ValueError(f'传入tuple的规格为{len(new_snap_shot)}，应该是3')
    if new_snap_shot[0] not in [0, 1, 2, 3, 4, 5]:
        raise TypeError(f'所传入的属性标号不正确！')
    # 存储不同属性类型的 AnomalyBar 对象

    # 直接使用缓存的 anomaly_bars 列表
    anomaly_bar = enemy.anomaly_bars_dict[new_snap_shot[0]]
    anomaly_bar.update_snap_shot(new_snap_shot)
