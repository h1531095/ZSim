import asyncio
import json
import os
import threading
from datetime import datetime

from .buff_handler import dump_buff_csv, report_buff_to_queue # noqa: F401
from .log_handler import async_log_writer, log_queue, report_to_log  # noqa: F401
from .result_handler import async_result_writer, result_queue, report_dmg_result    # noqa: F401

__result_id: int | None = None
__event_loop = None  # 存储事件循环的引用


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
        with open(cache_path, "w") as f:
            json.dump({}, f, indent=4)
    # 读取缓存文件
    with open(cache_path, "r+") as f:
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
        id_cache_dict[str(current_id)] = datetime.now().strftime("%Y-%m-%d_%H%M")

        f.seek(0)
        # 将更新后的缓存字典写回文件
        json.dump(id_cache_dict, f, indent=4)
        # 截断文件到当前写入位置
        f.truncate()
        # 更新全局结果ID
        __result_id = current_id


def start_async_tasks():
    """启动异步任务处理日志和结果写入"""
    global __event_loop

    # 如果已有事件循环在运行，则不再创建新的
    if __event_loop is not None:
        return

    # 创建新的事件循环
    __event_loop = asyncio.new_event_loop()

    # 在新线程中运行事件循环
    def run_event_loop():
        asyncio.set_event_loop(__event_loop)
        __event_loop.create_task(async_log_writer(__result_id))
        __event_loop.create_task(async_result_writer(__result_id))
        __event_loop.run_forever()

    loop_thread = threading.Thread(target=run_event_loop, daemon=True)
    loop_thread.start()


def start_report_threads(parallel_config):
    """用于在开始模拟时启动线程以处理日志和结果写入。"""
    if parallel_config is not None:
        run_turn_uuid = parallel_config.run_turn_uuid
    regen_result_id()
    start_async_tasks()


def stop_report_threads():
    dump_buff_csv(__result_id)
    log_queue.join()
    result_queue.join()
