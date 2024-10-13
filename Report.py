import os
import json
from datetime import datetime


def report_to_log(content):
    # 获取当前日期和时间
    if json.load(open('config.json')).get('debug'):
        now = datetime.now()
        timestamp = now.strftime(r'%Y-%m-%d_%H%M%S')
        report_file_path = f'./logs/{timestamp}.log'

        # 确保目录存在
        os.makedirs(os.path.dirname(report_file_path), exist_ok=True)

        # 写入日志
        with open(report_file_path, 'a', encoding='utf-8') as file:
            file.write(content + '\n')
