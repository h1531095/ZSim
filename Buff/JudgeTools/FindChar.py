def find_char(CID: int, char_list: list):
    for _ in char_list:
        if _.CID == CID:
            return _
    else:
        raise ValueError(f'并未找到CID为{CID}的角色！')