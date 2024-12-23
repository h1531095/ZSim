def find_char_from_name(NAME: str, char_list: list):
    for _ in char_list:
        if _.NAME == NAME:
            return _
    else:
        raise ValueError(f'并未找到Name为{NAME}的角色！')