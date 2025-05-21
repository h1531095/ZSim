import argparse
import timeit

from sim_progress.Report import stop_report_threads
from simulator.main_loop import main_loop
from simulator.dataclasses import SimCfg

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="ZZZ模拟器")
    parser.add_argument(
        "--stop-tick", type=int, default=None, help="指定模拟的tick数量 int"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="normal",
        choices=["normal", "parallel"],
        help="运行模式",
    )
    parser.add_argument(
        "--func",
        type=str,
        default=None,
        choices=["attr_curve", "weapon"],
        help="功能选择",
    )
    parser.add_argument(
        "--adjust-char",
        type=int,
        default=None,
        choices=[1, 2, 3],
        help="调整的角色相对位置",
    )
    parser.add_argument(
        "--sc-name", type=str, default=None, help="要调整的副词条名称 str"
    )
    parser.add_argument(
        "--sc-value", type=int, default=None, help="要调整的副词条数量 int"
    )
    parser.add_argument(
        "--run-turn-uuid", type=str, default=None, help="运行的uuid str"
    )
    parser.add_argument(
        "--remove-equip",
        action="store_true",
        default=False,
        help="移除装备 (存在此标志时移除)",
    )
    
    parser.add_argument(
        "--weapon-name",
        type=str,
        default=None,
        help="要调整的武器名称 str",
    )
    
    parser.add_argument(
        "--weapon-level",
        type=int,
        default=None,
        help="要调整的武器精炼等级 int",
    )

    # 解析命令行参数
    args = parser.parse_args()
    if args.mode == "normal":
        print("常规模式")
        # 常规模式，作为单进程运行，读取全部的配置
        if args.stop_tick is not None:
            print(
                f"\n主循环耗时: {timeit.timeit(lambda: main_loop(args.stop_tick), globals=globals(), number=1):.2f} s"
            )
        else:
            print(
                f"\n主循环耗时: {timeit.timeit(main_loop, globals=globals(), number=1):.2f} s"
            )

        print("\n正在等待IO结束···")
        stop_report_threads()
    elif args.mode == "parallel":
        print("并行模式")
        print(args)
        # 并行模式，作为子进程运行，角色的指定副词条将被设为传入值，并根据是否移除其他主副词条进行模拟
        sim_cfg: SimCfg = SimCfg(
            func=args.func,
            adjust_char=args.adjust_char,
            sc_name=args.sc_name,
            sc_value=args.sc_value,
            run_turn_uuid=args.run_turn_uuid,
            remove_equip=args.remove_equip,
            weapon_name=args.weapon_name,
            weapon_level=args.weapon_level,
        )
        if args.stop_tick is not None:
            print(
                f"\n主循环耗时: {timeit.timeit(lambda: main_loop(args.stop_tick, sim_cfg=sim_cfg), globals=globals(), number=1):.2f} s"
            )
        else:
            print(
                f"\n主循环耗时: {timeit.timeit(lambda: main_loop(sim_cfg=sim_cfg), globals=globals(), number=1):.2f} s"
            )
        stop_report_threads()

# TODO：Buff晚记录了1tick——虎皮来改
# TODO：属性抗性会影响失衡的积累速度，以及属性异常值的积累速度，这两个地方要修改
# TODO：异常伤害也不太对，算出来的低于实战值。初步怀疑是异常伤害的计算方式有问题，比如没有考虑labels的影响，明天可以用安比只平A打出感电试试看
