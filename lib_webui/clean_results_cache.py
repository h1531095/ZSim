import json
import os

try:
    from define import ID_CACHE_JSON
except ModuleNotFoundError:
    from .constants import ID_CACHE_JSON

from .constants import results_dir
id_cache_path = ID_CACHE_JSON

# 定义清理结果缓存的函数
def get_all_results(id_cache_path = ID_CACHE_JSON, results_dir = results_dir) -> dict[str: str|int|None]:
    # 读取id_cache.json文件
    with open(id_cache_path, 'r') as f:
        id_cache = json.load(f)

    # 获取results文件夹内的所有文件夹名
    folder_names = [name for name in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, name))]

    # 找出需要删除的key
    keys_to_delete = []
    for key in list(id_cache.keys()):
        if key not in folder_names:
            keys_to_delete.append(key)

    # 删除无对应文件夹的key
    for key in keys_to_delete:
        del id_cache[key]

    # 找出需要新建的key
    for folder_name in folder_names:
        if folder_name not in id_cache.keys():
            id_cache[folder_name] = 'Unkown results'

    # 将更新后的id_cache写回id_cache.json文件
    with open(id_cache_path, 'w') as f:
        json.dump(id_cache, f, indent=4)
    
    return id_cache

if __name__ == '__main__':
    get_all_results()