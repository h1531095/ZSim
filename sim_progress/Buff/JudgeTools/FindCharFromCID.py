import sys


def find_char_from_CID(CID: int):
    main_module = sys.modules["__main__"]
    char_list = main_module.char_data.char_obj_list
    for char in char_list:
        if char.CID == CID:
            return char
    else:
        raise ValueError(f'并未找到CID为{CID}的角色！')