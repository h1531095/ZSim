from CharSet import character_set       # 录入角色配置信息的函数
from CharacterClass import Character    # Character类
from EnemyClass import Enemy
from EnemySet import enemy_set
from KCalculate import Kcal
from BuffClass import Buff
from Actionlist_test import testlist
from BuffExsist_Judge import buff_exsist_judge
charnum, charname_box, charactive_box, judgelist_set, keybox = character_set()
LOADING_BUFF_DICT = {}
"""
这个DICT是用来装每次事件中需要添加的所有buff的,由于角色box扩充到了3个甚至更多,所以原定的list格式不再适用.
为了能用一个容器装下所有需要加载的buff,甚至需要明确它们的去向,用以下格式来形成DICT\n
{
    受益者名称:buff的实例化, 
    受益者名称:buff的实例化……
}\n
注意,本DICT中的受益者名称必须严格和角色的名字相同,要不然它就无法与DYNAMIC_BUFF_LIST联动了!!!!!
"""   
# charnum是实际角色数量.charname_box 是三个角色名;而charactive_box是三个实例化的角色,
# judgelist_set是决定哪些buff和本次模拟有关的配置单,里面主要包括武器名,角色名以及驱动盘4件套,
# keybox也是服务于判断哪些buff需要参与本次模拟的,
# 最后两个传出的变量在计算环节和buff判断的轮询中不会用的,只在初始化时需要.

enemyactive = enemy_set()
exsistbuff_dict = buff_exsist_judge(charname_box, judgelist_set, keybox)     
# 关于exsistbuff_dict 的详细注释和作用,在BuffExsist_Judge里.
# 其结构为:{buff名A:实例化buffA, buff名B:实例化buffB......}
TIMETICK = 0
DYNAMIC_BUFF_DICT = {}
"""
格式举例\n
{
    '艾莲':{'on_field': True, 'dynamic_buff_list':['buff名_艾莲']}, 
    '苍角':{'on_field': False, 'dynamic_buff_list':['buff名_苍角']}
}
"""
CHARACTER_ORDER_DICT = {}
"""
格式举例\n
{
    'on_field':当前角色名,
    'next':下一位角色名,
    'previous':上一位角色名
}\n
角色名如果空缺，就使用'empty'\n
"""