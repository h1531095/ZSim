import pandas as pd


# 角色配置常量
default_chars = ["扳机", "丽娜", "零号·安比"]   # 这个值其实没啥意义，但是必须是三个角色，否则可能会报错
df = pd.read_csv('data/character.csv')
char_options = df['name'].drop_duplicates().tolist()

# 武器选项
df = pd.read_csv('data/weapon.csv')
weapon_options = df['weapon_ID'].drop_duplicates().tolist()

# 驱动盘套装选项
df = pd.read_csv('data/equip_set_2pc.csv')
equip_set_ids = df['set_ID'].drop_duplicates().dropna().tolist()
equip_set4_options = equip_set2_options = equip_set_ids

# 主词条选项
main_stat4_options = ['攻击力%', '生命值%', '防御力%', '暴击率%', '暴击伤害%', '异常精通']
main_stat5_options = ['攻击力%', '生命值%', '防御力%', '穿透率', '物理属性伤害%', '火属性伤害%', '冰属性伤害%', '电属性伤害%', '以太属性伤害%']
main_stat6_options = ['攻击力%', '生命值%', '防御力%', '异常掌控', '冲击力%', '能量自动回复%']

# 副词条最大值
sc_max_value = 40

# 计算结果缓存文件路径
ID_CACHE_JSON = './results/id_cache.json'
results_dir = './results'