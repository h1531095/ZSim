from .DetectEdges import detect_edge
from .FindCharFromCID import find_char_from_CID
from .FindMain import *
from .FindCharFromName import find_char_from_name
from .FindEquipper import find_equipper


def check_preparation(buff_0, **kwargs):
    """
    这是一个综合函数。根据传入的参数，来执行不同的内容。
    """
    # 先决条件检查
    if buff_0.history.record is None:
        raise ValueError(f'buff_0的record模块尚未初始化！！！')
    record = buff_0.history.record

    # 参数获取
    char_CID: int = kwargs.get("char_CID")
    char_NAME: str = kwargs.get("char_NAME")
    enemy = kwargs.get("enemy")
    sub_exist_buff_dict = kwargs.get("sub_exist_buff_dict")
    dynamic_buff_list = kwargs.get("dynamic_buff_list")
    action_stack = kwargs.get("action_stack")

    # 参数正确性检查
    if sub_exist_buff_dict and char_NAME is None and char_CID is None:
        raise ValueError(f'在查询sub_exist_buff_dict的同时，应保证传入char_CID与char_NAME中的一个参数')
    if char_CID is None and char_NAME is None and buff_0:
        raise ValueError(f'在传入buff_0参数的同时，应保证传入char_CID与char_NAME中的一个参数')

    # 函数主体部分
    if char_CID:
        if record.char is None:
            record.char = find_char_from_CID(char_CID)
    if char_NAME:
        if record.char is None:
            record.char = find_char_from_name(char_NAME)
    if sub_exist_buff_dict:
        if record.char is None:
            raise ValueError(f'在buff_0.history.record 中并未读取到对应的char')
        if record.sub_exist_buff_dict is None:
            record.sub_exist_buff_dict = find_exist_buff_dict()[record.char.NAME]
    if enemy:
        if record.enemy is None:
            record.enemy = find_enemy()
    if dynamic_buff_list:
        if record.dynamic_buff_list is None:
            record.dynamic_buff_list = find_dynamic_buff_list()
    if action_stack:
        if record.action_stack is None:
            record.action_stack = find_stack()
