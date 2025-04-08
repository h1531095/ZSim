import json
import toml
from pathlib import Path
from typing import NewType

ElementType = NewType("ElementType", int)
INVALID_ELEMENT_ERROR = "Invalid element type"
ID_CACHE_JSON = 'results/id_cache.json'

# 加载角色配置
data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)
char_config_file = data_dir / "character_config.toml"
saved_char_config = {}
if char_config_file.exists():
    with open(char_config_file, "r", encoding="utf-8") as f:
        saved_char_config = toml.load(f)
else:
    raise FileNotFoundError(f"Character config file {char_config_file} not found.")


_config = json.load(open('config.json',encoding="utf-8-sig"))

APL_MODE: bool = _config['apl_mode']['enabled']
SWAP_CANCEL: bool = _config['swap_cancel_mode']['enabled']
APL_PATH: str = _config['database']['APL_FILE_PATH']
APL_NA_ORDER_PATH: str = _config['apl_mode']['na_order']
ENEMY_RANDOM_ATTACK: str = _config['apl_mode']['enemy_random_attack']
ENEMY_ATTACK_RESPONSE: bool = _config['apl_mode']['enemy_attack_response']
ENEMY_ATTACK_METHOD_CONFIG: str = _config['apl_mode']['enemy_attack_method_config']
ENEMY_ATTACK_ACTION: str = _config['apl_mode']['enemy_attack_action_data']
#: 合轴操作完成度系数->根据前一个技能帧数的某个比例来延后合轴
SWAP_CANCEL_MODE_COMPLETION_COEFFICIENT: float = _config['swap_cancel_mode']['completion_coefficient']

#: 操作滞后系数->合轴操作延后的另一种迟滞方案，即固定值延后。
SWAP_CANCEL_MODE_LAG_TIME: float = _config['swap_cancel_mode']['lag_time']
CHARACTER_DATA_PATH: str = _config["database"]["CHARACTER_DATA_PATH"]
WEAPON_DATA_PATH: str = _config["database"]["WEAPON_DATA_PATH"]
EQUIP_2PC_DATA_PATH: str = _config["database"]["EQUIP_2PC_DATA_PATH"]
SKILL_DATA_PATH: str = _config["database"]["SKILL_DATA_PATH"]
ENEMY_DATA_PATH: str = _config["database"]["ENEMY_DATA_PATH"]
DEFAULT_SKILL_PATH: str = _config["database"]["DEFAULT_SKILL_PATH"]
CRIT_BALANCING: bool = _config["character"]["crit_balancing"]
DEBUG: bool = _config["debug"]["enabled"]
DEBUG_LEVEL: int = _config["debug"]["level"]
JUDGE_FILE_PATH: str = _config["database"]["JUDGE_FILE_PATH"]
EFFECT_FILE_PATH: str = _config["database"]["EFFECT_FILE_PATH"]
EXIST_FILE_PATH: str = _config["database"]["EXIST_FILE_PATH"]
BUFF_LOADING_CONDITION_TRANSLATION_DICT: dict = _config["translate"]
ENABLE_WATCHDOG = _config["watchdog"]["enabled"]
WATCHDOG_LEVEL = _config["watchdog"]["level"]
INPUT_ACTION_LIST = './data/计算序列.csv'
compare_methods_mapping = {
    '<': lambda a, b: a < b,
    '<=': lambda a, b: a <= b,
    '>': lambda a, b: a > b,
    '>=': lambda a, b: a >= b,
    '==': lambda a, b: a == b,
    '!=': lambda a, b: a != b
}
ANOMALY_MAPPING: dict[int:str] = {
    0: '强击',
    1: '灼烧',
    2: '碎冰',
    3: '感电',
    4: '侵蚀',
    5: '烈霜碎冰'
}

if __name__ == "__main__":
    # 打印全部CONSTANT变量名
    def print_constant_names_and_values():
        # 获取当前全局命名空间
        global_vars = globals()
        # 筛选出所有全大写的变量名及其值
        constant_names_and_values = {name: value for name, value in global_vars.items() if name.isupper()}
        # 打印这些变量名及其值
        for name, value in constant_names_and_values.items():
            print(f"{name}: {value}")

    print_constant_names_and_values()
