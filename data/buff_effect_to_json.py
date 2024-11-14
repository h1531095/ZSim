import pandas as pd
import json


def convert_csv_to_json(csv_file, json_file):
    # 读取 CSV 文件
    df = pd.read_csv(csv_file)

    # 初始化结果字典
    result = {}

    # 遍历 DataFrame 的每一行
    for index, row in df.iterrows():
        name = row['名称']
        value = {}

        # 处理 key-value 对
        for i in range(1, 21, 2):
            try:
                key = row[f'key{i}']
                val = row[f'value{i}']
                if pd.notna(key) and pd.notna(val):
                    value[key] = float(val)
            except KeyError:
                continue

        result[name] = value

    # 将结果字典写入 JSON 文件
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    csv_file = 'data/buff_effect.csv'
    json_file = 'data/buff_effect.json'
    convert_csv_to_json(csv_file, json_file)
    print(f"CSV文件已成功转换为JSON文件: {json_file}")
