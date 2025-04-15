import json
import os
import queue
import threading
from collections import defaultdict
from datetime import datetime

import numpy as np
import pandas as pd

from define import DEBUG, DEBUG_LEVEL, ElementType, ANOMALY_MAPPING

buffered_data: dict = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
log_queue: queue.Queue = queue.Queue()
result_queue: queue.Queue = queue.Queue()

__result_id: int | None = None

def regen_result_id() -> None:
    """
    重新生成结果ID并更新ID缓存文件。

    此函数从ID缓存文件中读取现有ID，找到最大的有效ID，然后生成一个新的ID。
    新的ID会被添加到ID缓存文件中，并更新为当前的结果ID。

    如果ID缓存文件不存在，函数会创建一个新的文件。
    如果文件内容不是有效的JSON格式，函数会将其视为空字典处理。

    生成的ID是一个整数，从0开始递增。每个ID会关联一个时间戳，记录其生成的时间。
    """
    from define import ID_CACHE_JSON
    cache_path = ID_CACHE_JSON
    global __result_id
    # 检查缓存文件是否存在，如果不存在则创建
    if not os.path.exists(cache_path):
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w') as f:
            json.dump({}, f, indent=4)
    # 读取缓存文件
    with open(cache_path, 'r+') as f:
        try:
            id_cache_dict = json.load(f)
        except json.decoder.JSONDecodeError:
            id_cache_dict = {}

        valid_ids = []
        # 筛选出有效的整数ID
        for key in id_cache_dict.keys():
            try:
                valid_ids.append(int(key))
            except ValueError:
                continue

        # 确定新的ID
        if valid_ids:
            current_id = max(valid_ids) + 1
        else:
            current_id = 0

        # 将新ID和当前时间戳添加到缓存字典中
        id_cache_dict[str(current_id)] = datetime.now().strftime('%Y-%m-%d_%H%M')

        f.seek(0)
        # 将更新后的缓存字典写回文件
        json.dump(id_cache_dict, f, indent=4)
        # 截断文件到当前写入位置
        f.truncate()
        # 更新全局结果ID
        __result_id = current_id


def prepare_to_report(rid: int):
    # 获取当前日期和时间
    report_file_path = f'./logs/{rid}.log'
    buff_report_file_path_pre = f'./results/{rid}/buff_log/'
    # 确保目录存在
    os.makedirs(os.path.dirname(report_file_path), exist_ok=True)
    os.makedirs(os.path.dirname(buff_report_file_path_pre), exist_ok=True)
    return report_file_path, buff_report_file_path_pre


def report_to_log(content: str | None = None, level=4) -> None:
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
        report_file_path, buff_report_file_path_pre = prepare_to_report(__result_id)
        buff_report_file_path = buff_report_file_path_pre + f'{char_name}.csv'
        df = pd.DataFrame.from_dict(buffered_data[char_name], orient='index').reset_index()
        df.rename(columns={'index': 'time_tick'}, inplace=True)
        # 对 'time_tick' 列进行排序
        df = df.sort_values(by='time_tick')
        # 保存更新后的 CSV 文件
        df.to_csv(buff_report_file_path, index=False, encoding='utf-8-sig')


def report_dmg_result(
        tick: int,
        element_type: ElementType | int,
        skill_tag: str | None = None,
        dmg_expect: float | np.float64 = 0,
        dmg_crit: float | np.float64 | None = None,
        is_anomaly: bool = False,
        is_disorder: bool = False,
        **kwargs
):
    if is_anomaly and skill_tag is None:
        skill_tag = ANOMALY_MAPPING.get(element_type, skill_tag)
    assert skill_tag is not None, '技能标签不能为空！'
    if is_disorder and '紊乱' not in skill_tag:
        skill_tag += '紊乱'
    if dmg_crit is None:
        dmg_crit = np.nan
    result_dict = {
        'tick': tick,
        'element_type': element_type,
        'is_anomaly': is_anomaly,
        'skill_tag': skill_tag,
        'dmg_expect': float(dmg_expect),
        'dmg_crit': float(dmg_crit),
    }
    result_dict.update(kwargs)
    result_queue.put(result_dict)


def thread_log_writer():
    report_file_path, _ = prepare_to_report(__result_id)
    while True:
        with open(report_file_path, 'a', encoding='utf-8') as file:
            content = log_queue.get()
            file.write(f"{content}\n")
        log_queue.task_done()


def thread_result_writer(rid):
    result_path = f'./results/{rid}/damage.csv'
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    new_file = not os.path.exists(result_path)
    while True:
        result_dict = result_queue.get()
        result_df = pd.DataFrame([result_dict])
        if new_file:
            result_df.to_csv(result_path, index=False, encoding='utf-8-sig')
            new_file = False
        else:
            result_df.to_csv(result_path, mode='a', header=False, index=False)
        result_queue.task_done()


def start_report_threads():
    """用于在开始模拟时启动线程以处理日志和结果写入。"""
    regen_result_id()
    log_writer_thread = threading.Thread(target=thread_log_writer, daemon=True)
    log_writer_thread.start()

    result_writer_thread = threading.Thread(target=lambda: thread_result_writer(__result_id), daemon=True)
    result_writer_thread.start()
