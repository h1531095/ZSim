import polars as pl
from define import ElementType


# 角色与CID映射表
def _init_char_mapping() -> dict:
    """初始化角色CID和名称的映射关系"""
    try:
        df = pl.scan_csv("./zsim/data/character.csv")
        mapping = df.select(["name", "CID"]).collect().to_dict(as_series=False)
        return {name: str(cid) for name, cid in zip(mapping["name"], mapping["CID"])}
    except Exception as e:
        print(f"Warning: Failed to load character mapping: {e}")
        return {}


CHAR_CID_MAPPING = _init_char_mapping()

# 角色配置常量
default_chars = [
    "扳机",
    "丽娜",
    "零号·安比",
]  # 这个值其实没啥意义，但是必须是三个角色，否则可能会报错
__lf = pl.scan_csv("./zsim/data/character.csv")
char_options = __lf.select("name").unique().collect().to_series().to_list()

# 武器选项
__lf = pl.scan_csv("./zsim/data/weapon.csv")
weapon_options = __lf.select("中文名称").unique().collect().to_series().to_list()

# 驱动盘套装选项
__lf = pl.scan_csv("./zsim/data/equip_set_2pc.csv")
equip_set_ids = (
    __lf.select("set_ID")
    .filter(pl.col("set_ID").is_not_null())
    .unique()
    .collect()
    .to_series()
    .to_list()
)
equip_set4_options = equip_set2_options = equip_set_ids

# 主词条选项
main_stat4_options = [
    "攻击力%",
    "生命值%",
    "防御力%",
    "暴击率%",
    "暴击伤害%",
    "异常精通",
    "-",
]
main_stat5_options = [
    "攻击力%",
    "生命值%",
    "防御力%",
    "穿透率",
    "物理属性伤害%",
    "火属性伤害%",
    "冰属性伤害%",
    "电属性伤害%",
    "以太属性伤害%",
    "-",
]
main_stat6_options = [
    "攻击力%",
    "生命值%",
    "防御力%",
    "异常掌控",
    "冲击力%",
    "能量自动回复%",
    "-",
]

stats_trans_mapping = {
    "攻击力%": "scATK_percent",
    "攻击力": "scATK",
    "生命值%": "scHP_percent",
    "生命值": "scHP",
    "防御力%": "scDEF_percent",
    "防御力": "scDEF",
    "异常精通": "scAnomalyProficiency",
    "穿透值": "scPEN",
    "暴击率": "scCRIT",
    "暴击伤害": "scCRIT_DMG",
    "属性伤害加成": "DMG_BONUS",
    "穿透率": "PEN_RATIO",
    "异常掌控": "ANOMALY_MASTERY",
    "能量自动回复": "SP_REGEN",
}

SC_DATA_DISCRIPTION_MAPPING = {
    "scATK_percent": "3%/词条",
    "scATK": "19点/词条",
    "scHP_percent": "3%/词条",
    "scHP": "112/词条",
    "scDEF_percent": "4.8%/词条",
    "scDEF": "15点/词条",
    "scAnomalyProficiency": "9点/词条",
    "scPEN": "9点/词条",
    "scCRIT": "2.4%暴击率或4.8%暴击伤害/词条",
    "scCRIT_DMG": "2.4%暴击率或4.8%暴击伤害/词条",
    "DMG_BONUS": "3%/词条",
    "PEN_RATIO": "2.4%/词条",
    "ANOMALY_MASTERY": "3%/词条",
    "SP_REGEN": "6%/词条",
}

# 副词条最大值
sc_max_value = 40

# 计算结果缓存文件路径
ID_CACHE_JSON = "./results/id_cache.json"
results_dir = "./results"

# 六元素翻译对应表
element_mapping: dict[ElementType | str] = {
    0: "物理",
    1: "火",
    2: "冰",
    3: "电",
    4: "以太",
    5: "烈霜",
}


# ID重复时抛出的自定义异常类
class IDDuplicateError(Exception):
    """当检测到重复ID时抛出此异常"""

    pass


del __lf  # 确保在文件末尾删除临时变量
