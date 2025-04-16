import timeit
from sim_progress import Report
from simulator.main_loop import main_loop
from sim_progress.Report import write_to_csv


if __name__ == '__main__':
    print(f'\n主循环耗时: {timeit.timeit(main_loop, globals=globals(), number=1):.2f} s')
    # main_loop(6000)
    print('\n正在等待IO结束···')
    write_to_csv()
    Report.log_queue.join()
    Report.result_queue.join()

# TODO：Buff晚记录了1tick——虎皮来改
# TODO：属性抗性会影响失衡的积累速度，以及属性异常值的积累速度，这两个地方要修改
# TODO：异常伤害也不太对，算出来的低于实战值。初步怀疑是异常伤害的计算方式有问题，比如没有考虑labels的影响，明天可以用安比只平A打出感电试试看
