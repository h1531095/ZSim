from typing import Iterator

from run import MainArgs


def generate_parallel_args(
    stop_tick: int,
    parallel_cfg: dict,
    run_turn_uuid: str,
    stats_trans_mapping: dict,
) -> Iterator[MainArgs]:
    """生成用于并行模拟的参数。

    Args:
        stop_tick: 模拟停止的 tick 数。
        parallel_cfg: 并行模式的配置字典。
        run_turn_uuid: 当前运行轮次的 UUID。
        stats_trans_mapping: 属性名称到内部名称的映射。

    Yields:
        MainArgs: 为每个模拟任务生成的参数对象。
    """
    adjust_sc_cfg = parallel_cfg["adjust_sc"]
    sc_list = adjust_sc_cfg["sc_list"]
    sc_range_start, sc_range_end = adjust_sc_cfg["sc_range"]
    remove_equip_list = adjust_sc_cfg.get(
        "remove_equip_list", []
    )  # 获取需要移除装备的词条列表，如果不存在则为空列表
    for sc_name in sc_list:
        for sc_value in range(sc_range_start, sc_range_end + 1):
            args = MainArgs()
            args.stop_tick = stop_tick
            args.mode = "parallel"
            args.adjust_char = parallel_cfg["adjust_char"]  # 添加调整角色参数
            args.sc_name = stats_trans_mapping[sc_name]
            args.sc_value = sc_value
            args.run_turn_uuid = run_turn_uuid  # 设置统一的UUID
            # 检查当前 sc_name 是否在 remove_equip_list 中
            if sc_name in remove_equip_list:
                args.remove_equip = True
            else:
                args.remove_equip = False  # 默认不移除装备
            yield args
