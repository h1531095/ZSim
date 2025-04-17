import pandas as pd
from define import ElementType

# 角色与CID映射表
def _init_char_mapping() -> dict:
        """初始化角色CID和名称的映射关系"""
        try:
            df = pd.read_csv('./zsim/data/character.csv')
            mapping = {}
            for _, row in df.iterrows():
                cid = str(row['CID'])
                name = row['name']
                mapping[cid] = name
                mapping[name] = cid
            return mapping
        except Exception as e:
            print(f"Warning: Failed to load character mapping: {e}")
            return {}
CHAR_CID_MAPPING = _init_char_mapping()

# 角色配置常量
default_chars = ["扳机", "丽娜", "零号·安比"]   # 这个值其实没啥意义，但是必须是三个角色，否则可能会报错
__df = pd.read_csv('./zsim/data/character.csv')
char_options = __df['name'].drop_duplicates().tolist()

# 武器选项
__df = pd.read_csv('./zsim/data/weapon.csv')
weapon_options = __df['weapon_ID'].drop_duplicates().tolist()

# 驱动盘套装选项
__df = pd.read_csv('./zsim/data/equip_set_2pc.csv')
equip_set_ids = __df['set_ID'].drop_duplicates().dropna().tolist()
equip_set4_options = equip_set2_options = equip_set_ids

# 主词条选项
main_stat4_options = ['攻击力%', '生命值%', '防御力%', '暴击率%', '暴击伤害%', '异常精通', '-']
main_stat5_options = ['攻击力%', '生命值%', '防御力%', '穿透率', '物理属性伤害%', '火属性伤害%', '冰属性伤害%', '电属性伤害%', '以太属性伤害%', '-']
main_stat6_options = ['攻击力%', '生命值%', '防御力%', '异常掌控', '冲击力%', '能量自动回复%', '-']

# 副词条最大值
sc_max_value = 40

# 计算结果缓存文件路径
ID_CACHE_JSON = './results/id_cache.json'
results_dir = './results'

# 六元素翻译对应表
element_mapping: dict[ElementType | str] = {
    0: "物理",
    1: "火",
    2: "冰",
    3: "电",
    4: "以太",
    5: "烈霜"
}

# ID重复时抛出的自定义异常类
class IDDuplicateError(Exception):
    """当检测到重复ID时抛出此异常"""
    pass



del __df    # 确保在文件末尾删除临时变量