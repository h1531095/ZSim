import importlib
import os


# # 获取当前文件夹下所有的py文件并加载
# buff_logic_directory = os.path.dirname(__file__)
# # 遍历目录下的每一个文件
# for filename in os.listdir(buff_logic_directory):
#     if filename.endswith('.py') and filename != '__init__.py':
#         # 获取模块名，去掉.py后缀
#         module_name = f"BuffXLogic.{filename[:-3]}"
#         try:
#             # 动态导入模块
#             importlib.import_module(module_name)
#         except ImportError as e:
#             print(f"Failed to import {module_name}: {e}")
