def BonusCal(basic, bonus_list):
    if len(bonus_list) != 2:
        raise ValueError('bonus_list必须包含2个元素！')
    fix = bonus_list[0]
    bonus = bonus_list[1]
    result = basic * (1 + bonus) + fix
    return result
