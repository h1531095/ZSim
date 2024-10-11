import os
report_file_path = './log.txt'
def report_to_log(content:str):
    with open(report_file_path, 'a') as file:
        file.write(content + '\n')
