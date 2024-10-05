def BonusCal(basic, bonuslist):
    if len(bonuslist) != 2:
        raise ValueError('bonus_list必须包含2个元素！')
    fix = bonuslist[0]
    bonus = bonuslist[1]
    result = basic * (1 + bonus) + fix
    return result