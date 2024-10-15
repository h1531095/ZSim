import json
import pandas as pd


_config = json.load(open('config.json'))

CHARACTER_DATA_PATH: str = _config["database"]["CHARACTER_DATA_PATH"]
WEAPON_DATA_PATH: str = _config["database"]["WEAPON_DATA_PATH"]
EQUIP_2PC_DATA_PATH: str = _config["database"]["EQUIP_2PC_DATA_PATH"]
SKILL_DATA_PATH: str = _config["database"]["SKILL_DATA_PATH"]
DEFAULT_SKILL_PATH: str = _config["database"]["DEFAULT_SKILL_PATH"]
CRIT_BALANCING: bool = _config["character"]["crit_balancing"]
DEBUG: bool = _config["debug"]
JUDGE_FILE_PATH: str = _config["database"]["JUDGE_FILE_PATH"]
EFFECT_FILE_PATH: str = _config["database"]["EFFECT_FILE_PATH"]
EXIST_FILE_PATH: str = _config["database"]["EXIST_FILE_PATH"]
BUFF_LOADING_CONDITION_TRANSLATION_DICT: dict = _config["translate"]
EXIST_FILE = pd.read_csv(EXIST_FILE_PATH, index_col='BuffName')
JUDGE_FILE = pd.read_csv(JUDGE_FILE_PATH, index_col='BuffName')
EFFECT_FILE = pd.read_csv(EFFECT_FILE_PATH, index_col='BuffName')



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
