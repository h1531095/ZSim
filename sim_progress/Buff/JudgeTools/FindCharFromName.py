import sys


def find_char_from_name(NAME: str):
    main_module = sys.modules["__main__"]
    char_list = main_module.char_data.char_obj_list
    for _ in char_list:
        if _.NAME == NAME:
            return _
    else:
        raise ValueError(f"未找到名为{NAME}的角色")
