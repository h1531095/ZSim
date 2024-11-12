import json
import os
import queue
import threading
from collections import defaultdict
from datetime import datetime

import numpy as np
import pandas as pd
from tqdm import trange

from RandomNumberGenerator import MAX_SIGNED_INT64
from define import DEBUG, DEBUG_LEVEL, ElementType

buffered_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
log_queue = queue.Queue()
result_queue = queue.Queue()

def prepare_to_report():
    # 获取当前日期和时间
    now = datetime.now()
    timestamp = now.strftime(r'%Y-%m-%d_%H%M')
    report_file_path = f'./logs/{timestamp}.log'
    buff_report_file_path_pre = f'./logs/BuffLog/{timestamp}_'
    # 确保目录存在
    os.makedirs(os.path.dirname(report_file_path), exist_ok=True)
    return report_file_path, buff_report_file_path_pre


def report_to_log(content:str = None, level=4) -> None:
    """
    如果满足调试级别要求 DEBUG_LEVEL <= level，则将指定内容写入日志文件中。

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

    if not DEBUG or content is None:
        return

    if DEBUG and DEBUG_LEVEL <= level:
        # 写入日志
        log_queue.put(content)


def report_buff_to_log(character_name: str, time_tick, buff_name: str, buff_count, all_match: bool, level=4):
    if DEBUG and DEBUG_LEVEL <= level:
        if all_match:
            buffered_data[character_name][time_tick][buff_name] += buff_count


def write_to_csv():
    for char_name in buffered_data:
        if char_name not in buffered_data:
            raise ValueError('你tmd函数写错了！')
        report_file_path, buff_report_file_path_pre = prepare_to_report()
        buff_report_file_path = buff_report_file_path_pre + f'{char_name}.csv'
        df = pd.DataFrame.from_dict(buffered_data[char_name], orient='index').reset_index()
        df.rename(columns={'index': 'time_tick'}, inplace=True)
        # 对 'time_tick' 列进行排序
        df = df.sort_values(by='time_tick')
        # 保存更新后的 CSV 文件
        df.to_csv(buff_report_file_path, index=False)

def get_result_id() -> int:
    from define import ID_CACHE_JSON
    cache_path = ID_CACHE_JSON
    if not os.path.exists(cache_path):
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w') as f:
            json.dump({}, f, indent=4)
    with open (cache_path, 'r+') as f:
        try:
            id_cache_dict = json.load(f)
        except json.decoder.JSONDecodeError:
            id_cache_dict = {}
        id_lst = list(id_cache_dict.keys())
        if id_lst:
            current_id = int(id_lst[-1]) + 1
        else:
            current_id = 0
        id_cache_dict[str(current_id)] = datetime.now().strftime('%Y-%m-%d_%H%M')
        f.seek(0)
        json.dump(id_cache_dict, f, indent=4)
        f.truncate()
        return current_id

def report_dmg_result(
        tick: int,
        element_type: ElementType | int,
        skill_tag: str = None,
        dmg_expect: float | np.float64 = 0,
        dmg_crit: float | np.float64 = None,
        is_anomaly: bool = False,
        is_disorder: bool = False,
        **kwargs
        ):
    if is_anomaly:
        match element_type:
            case 0:
                skill_tag = '强击'
            case 1:
                skill_tag = '灼烧'
            case 2:
                skill_tag = '碎冰'
            case 3:
                skill_tag = '感电'
            case 4:
                skill_tag = '侵蚀'
    if is_disorder:
        skill_tag += '紊乱'
    if dmg_crit is None:
        dmg_crit = 'nan'
    result_dict = {
        'tick': tick,
        'element_type': element_type,
        'skill_tag': skill_tag,
        'dmg_expect': float(dmg_expect),
        'dmg_crit': float(dmg_crit),
    }
    result_dict.update(kwargs)
    result_queue.put(result_dict)



def thread_log_writer():
    report_file_path, _ = prepare_to_report()
    while True:
        with open(report_file_path, 'a', encoding='utf-8') as file:
            content = log_queue.get()
            file.write(f"{content}\n")
        log_queue.task_done()

def thread_result_writer(rid = get_result_id()):
    result_path = f'./results/{rid}.csv'
    new_file = os.path.exists(result_path)
    while True:
        result_dict = result_queue.get()
        result_df = pd.DataFrame([result_dict])
        if new_file:
            result_df.to_csv(result_path, mode='a', header=False, index=False)
        else:
            result_df.to_csv(result_path, index=False)
            new_file = True
        result_queue.task_done()

log_writer_thread = threading.Thread(target=thread_log_writer, daemon=True)
log_writer_thread.start()


result_writer_thread = threading.Thread(target=thread_result_writer, daemon=True)
result_writer_thread.start()



if __name__ == '__main__':

    for i in trange(10000):
        report_dmg_result(tick = i, element_type=0, skill_tag='test', dmg_expect=MAX_SIGNED_INT64, dmg_crit=MAX_SIGNED_INT64)

