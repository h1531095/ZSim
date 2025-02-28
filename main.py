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
