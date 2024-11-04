import os
from datetime import datetime
from define import DEBUG, DEBUG_LEVEL
import pandas as pd
from collections import defaultdict
buffered_data = defaultdict(lambda: defaultdict(int))


def prepare_to_report():
    # 获取当前日期和时间
    now = datetime.now()
    timestamp = now.strftime(r'%Y-%m-%d_%H%M')
    report_file_path = f'./logs/{timestamp}.log'
    buff_report_file_path_pre = f'./logs/BuffLog/{timestamp}_'
    # 确保目录存在
    os.makedirs(os.path.dirname(report_file_path), exist_ok=True)
    return report_file_path, buff_report_file_path_pre


def report_to_log(content, level=4):
    """
    如果满足调试级别要求 DEBUG_LEVEL >= level，则将指定内容写入日志文件中。

    参数:
    - content: 要写入日志文件的内容。
    - level: 日志级别，用于判断是否应该记录该日志。级别从 0 到 4，4 为最高级别。
        0：不重要
        1：可能需要注意
        2：需要注意
        3：非常有必要输出
        4：必须要输出日志

    该函数首先检查当前是否处于DEBUG模式以及日志的DEBUG_LEVEL是否大于等于当前日志级别。
    如果检查通过，则生成一个带有当前日期和时间戳的日志文件名，并确保对应的日志目录存在。
    最后，将content写入到日志文件中。
    """
    if DEBUG and DEBUG_LEVEL >= level:
        report_file_path, buff_report_file_path_pre = prepare_to_report()
        # 写入日志
        with open(report_file_path, 'a', encoding='utf-8-sig') as file:
            file.write(f"{content}\n")


def report_buff_to_log(time_tick: str, buff_name: str, buff_count, all_match: bool, level=4):
    if DEBUG and DEBUG_LEVEL >= level:
        if all_match:
            buffered_data[time_tick][buff_name] += buff_count


def write_to_csv(char_name: str):
    report_file_path, buff_report_file_path_pre = prepare_to_report()
    buff_report_file_path = buff_report_file_path_pre + f'{char_name}.csv'
    df = pd.DataFrame.from_dict(buffered_data, orient='index').reset_index()
    df.rename(columns={'index': 'time_tick'}, inplace=True)
    # 对 'time_tick' 列进行排序
    df = df.sort_values(by='time_tick')
    # 保存更新后的 CSV 文件
    df.to_csv(buff_report_file_path, index=False)


if __name__ == '__main__':
    report_to_log('test', level=4)

# TODO: 彻底实现三个角色分别生成三个缓存，并且最后录入三个csv并保存的功能。