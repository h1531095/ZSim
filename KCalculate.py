def Kcal(character):
    level = int(character.info.level)
    k = 0.1551 * level ** 2 + 3.141 * level + 47.2039
    print(f'当前进攻方等级系数是：{k}')
    return k
