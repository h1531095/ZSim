import timeit
import argparse
from simulator.main_loop import main_loop
from sim_progress.Report import stop_report_threads


if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="ZZZ模拟器")
    parser.add_argument(
        "--stop_tick", type=int, default=None, help="指定模拟的tick数量"
    )

    # 解析命令行参数
    args = parser.parse_args()

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

# TODO：Buff晚记录了1tick——虎皮来改
# TODO：属性抗性会影响失衡的积累速度，以及属性异常值的积累速度，这两个地方要修改
# TODO：异常伤害也不太对，算出来的低于实战值。初步怀疑是异常伤害的计算方式有问题，比如没有考虑labels的影响，明天可以用安比只平A打出感电试试看
