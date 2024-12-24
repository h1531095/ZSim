def find_char_from_name(NAME: str, char_list: list):
    for char in char_list:
        if char.NAME == NAME:
            return char
    else:
        raise ValueError(f'并未找到Name为{NAME}的角色！')