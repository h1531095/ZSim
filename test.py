import pandas as pd

from Report import report_to_log
from define import EFFECT_FILE_PATH


def __lookup_buff_effect(index: str) -> dict:
    """
    根据索引获取buff效果字典。

    该方法从CSV文件中读取所有buff效果数据，并查找首列值为指定索引的行。
    找到后，将该行的数据转换为字典并返回。

    参数:
    - index: buff索引。

    返回:
    - buff_effect: 包含buff效果的字典。
    """
    # 初始化一个空的字典来存储buff效果
    buff_effect = {}
    # 读取包含所有buff效果的CSV文件
    all_buff_df = pd.read_csv(EFFECT_FILE_PATH)
    try:
        row = all_buff_df[all_buff_df['BuffName'] == index].to_dict("records")
        row = row[0]
    except IndexError | KeyError as e:
        row = {}
        report_to_log(f'[WARNING] {e}: 索引{index}没有找到，或buff效果csv结构错误', level=4)

    if row:
        for key, value in row.items():
            if value == 0:
                continue
            else:
                buff_effect[key]: float = value
    return buff_effect

if __name__ == '__main__':
    print(__lookup_buff_effect('test'))