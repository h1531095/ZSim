from CharSet import character_set       # 录入角色配置信息的函数
# from CharacterClass import Character    # Character类
from CharSet_new import Character
from EnemySet import enemy_set
from BuffExist_Judge import buff_exist_judge

charnum, charname_box, char_active_box, judgelist_set, keybox = character_set()
# charnum是实际角色数量.charname_box 是三个角色名;而charactive_box是三个实例化的角色,
# judgelist_set是决定哪些buff和本次模拟有关的配置单,里面主要包括武器名,角色名以及驱动盘4件套,
# keybox也是服务于判断哪些buff需要参与本次模拟的,
# 最后两个传出的变量在计算环节和buff判断的轮询中不会用的,只在初始化时需要.


def create_char_dict(char1: Character, char2: Character = None, char3:Character = None):
    """
    创建字典：
    {角色名：角色对象}
    对于空位生成一个占位符（类型待定）
    """
    char_dict = {}
    for char in [char1, char2, char3]:
        try:
            char_dict[char.NAME] = char
        except:
            char_dict[id(char)] = 'empty'
            
    return char_dict


enemyactive = enemy_set()
exsistbuff_dict = buff_exist_judge(charname_box, judgelist_set, keybox)
# 关于exsistbuff_dict 的详细注释和作用,在BuffExsist_Judge里.
# 其结构为:{buff名A:实例化buffA, buff名B:实例化buffB......}
DYNAMIC_BUFF_DICT = {'艾莲': {'在前台': True, 'dynamic_buff_list': ['buff名_艾莲']},  '苍角': {'在前台': False, 'dynamic_buff_list': ['buff名_苍角']}}