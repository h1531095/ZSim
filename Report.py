import os
from datetime import datetime
from define import DEBUG, DEBUG_LEVEL


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
        # 获取当前日期和时间
        now = datetime.now()
        timestamp = now.strftime(r'%Y-%m-%d_%H%M')
        report_file_path = f'./logs/{timestamp}.log'

        # 确保目录存在
        os.makedirs(os.path.dirname(report_file_path), exist_ok=True)

        # 写入日志
        with open(report_file_path, 'a', encoding='utf-8-sig') as file:
            file.write(f"{content}\n")


if __name__ == '__main__':
    report_to_log('test', level=4)
