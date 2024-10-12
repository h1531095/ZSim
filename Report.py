import os
from datetime import datetime

def report_to_log(content):
    # 获取当前日期和时间
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    report_file_path = f'./logs/{timestamp}.log'

    # 确保目录存在
    os.makedirs(os.path.dirname(report_file_path), exist_ok=True)

    # 写入日志
    with open(report_file_path, 'a') as file:
        file.write(content + '\n')
