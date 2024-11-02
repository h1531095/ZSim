import os
from datetime import datetime
from define import DEBUG, DEBUG_LEVEL
import pandas as pd


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


def report_buff_to_log(char_name: str, time_tick: str, action_name: str, sub_mission: str, buff_name: str, buff_count, all_match: bool, level=4):
    if DEBUG and DEBUG_LEVEL >= level:
        report_file_path, buff_report_file_path_pre = prepare_to_report()
        buff_report_file_path = buff_report_file_path_pre + f'{char_name}.csv'

        # 检查文件是否已存在
        if os.path.exists(buff_report_file_path):
            df = pd.read_csv(buff_report_file_path)

            # 检查 buff_name 是否已经在列名中
            if buff_name not in df.columns:
                df[buff_name] = None
        else:
            df = pd.DataFrame(columns=['time_tick', 'action name', 'sub_mission', buff_name])

        # 创建新行
        new_row = {'time_tick': time_tick, 'action name': action_name, 'sub_mission': sub_mission}
        new_row[buff_name] = buff_count if all_match else None

        # 过滤掉所有值为空的列
        new_row_filtered = {k: v for k, v in new_row.items() if v is not None}

        # 仅在 new_row_filtered 有数据时合并
        if new_row_filtered:
            df = pd.concat([df, pd.DataFrame([new_row_filtered])], ignore_index=True)

        # 合并相同 time_tick 的行
        df = df.groupby(['time_tick', 'action name', 'sub_mission'], as_index=False).agg(lambda x: x.sum() if x.notnull().any() else None)

        # 保存更新后的 CSV 文件
        df.to_csv(buff_report_file_path, index=False)


if __name__ == '__main__':
    report_to_log('test', level=4)
