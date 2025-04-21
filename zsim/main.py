import argparse
import timeit

from sim_progress.Report import stop_report_threads
from simulator.main_loop import main_loop
from simulator.dataclasses import ParallelConfig

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="ZZZ模拟器")
    parser.add_argument(
        "--stop_tick", type=int, default=None, help="指定模拟的tick数量 int"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="normal",
        choices=["normal", "parallel"],
        help="运行模式",
    )
    parser.add_argument(
        "--adjust_char",
        type=int,
        default=None,
        choices=[1, 2, 3],
        help="调整的角色相对位置",
    )
    parser.add_argument("--sc_name", type=str, default=None, help="要调整的副词条名称 str")
    parser.add_argument("--sc_value", type=int, default=None, help="要调整的副词条数量 int")
    parser.add_argument("--run_turn_uuid", type=str, default=None, help="运行的uuid str")
    parser.add_argument("--remove_equip", type=bool, default=True, help="移除装备 bool")

    # 解析命令行参数
    args = parser.parse_args()
    print(args)
    if args.mode == "normal":
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
        # 并行模式，作为子进程运行，角色的指定副词条将被设为传入值，并根据是否移除其他主副词条进行模拟
        parallel_config: ParallelConfig = ParallelConfig(
            adjust_char=args.adjust_char,
            sc_name=args.sc_name,
            sc_value=args.sc_value,
            run_turn_uuid=args.run_turn_uuid,
            remove_equip=args.remove_equip,
        )
        if args.stop_tick is not None:
            print(
                f"\n主循环耗时: {timeit.timeit(lambda: main_loop(args.stop_tick, parallel_config=parallel_config), globals=globals(), number=1):.2f} s"
            )
        else:
            print(
                f"\n主循环耗时: {timeit.timeit(lambda: main_loop(parallel_config=parallel_config), globals=globals(), number=1):.2f} s"
            )
        stop_report_threads()

# TODO：Buff晚记录了1tick——虎皮来改
# TODO：属性抗性会影响失衡的积累速度，以及属性异常值的积累速度，这两个地方要修改
# TODO：异常伤害也不太对，算出来的低于实战值。初步怀疑是异常伤害的计算方式有问题，比如没有考虑labels的影响，明天可以用安比只平A打出感电试试看
