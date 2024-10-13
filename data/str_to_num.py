import os
import csv
from decimal import Decimal

'''
用于将./data 目录下的csv重整
'''


def is_percentage(value):
    """检查字符串是否为百分比形式"""
    return isinstance(value, str) and '%' in value


def convert_percentage(value):
    """将百分比字符串转换为浮点数"""
    return float(Decimal(value.strip('%')) / 100)


def process_cell(value):
    """处理单个单元格的值"""
    if is_percentage(value):
        try:
            return convert_percentage(value)
        except:
            return value
    try:
        return eval(value)
    except:
        return value


def process_csv_file(file_path):
    """处理单个 CSV 文件"""
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # 处理除首行首列外的数据
    for row_index in range(1, len(rows)):
        for col_index in range(1, len(rows[row_index])):
            rows[row_index][col_index] = process_cell(rows[row_index][col_index])

    # 将处理后的数据写回文件
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def process_all_csv_files(directory):
    """处理指定目录下的所有 CSV 文件"""
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            process_csv_file(file_path)


if __name__ == '__main__':
    directory = './data'
    process_all_csv_files(directory)
