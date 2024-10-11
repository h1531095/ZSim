import json
from EnemyClass import Enemy
from Parameter import get_parameter
enemysetkeys = ['ID', 'Name', 'Type', 'Level', 
                'Hp', 'Atk', 'Def', 'Stun', 'StunDamageTakeRatio', 'StunResetCount', 'ElementAbnormal',
                'PhyResist', 'FireResist', 'IceResist', 'EleResist', 'EthResist']
def enemy_set():
    print('当前已激活的敌人配置方案如下：')
    with open('.\EnemyConfig.json', 'r', encoding='utf-8') as file:
        enemyconfig_dict = json.load(file)
    #把enemyconfig_dict中的键值提取出来，变成一个列表，放到enemyconfig_key 中
    enemyconfig_key = list(a for a in enemyconfig_dict) 

    #取enemyconfig_key的长度
    enemyconfigcount = len(enemyconfig_key)

    #显示目前所有方案
    for i in range(enemyconfigcount):
        print(f'{i+1}', enemyconfig_key[i])

    #选择敌人方案序号，并判断输入是否正确
    enemyconfig_number = get_parameter('请输入要选择的敌人配置方案序号：', lambda x: 0 <= int(x) <= enemyconfigcount)
    enemyconfig_number = int(enemyconfig_number)

    enemyconfig_valuelist = enemyconfig_dict[enemyconfig_key[enemyconfig_number - 1]]
    enemyconfig_now = dict(zip(enemysetkeys, enemyconfig_valuelist))
    
    #把怪物属性通过Enemy类进行实例化，并且放到Enemyactive里面
    Enemyactive = Enemy(enemyconfig_now)
    print(f'当前激活的敌人是：{Enemyactive.info.name}')
    return Enemyactive