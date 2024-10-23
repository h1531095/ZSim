import pandas as pd
import json
from BuffClass import Buff
from define import EXIST_FILE_PATH, JUDGE_FILE_PATH


EXIST_FILE = pd.read_csv(EXIST_FILE_PATH, index_col='BuffName')
JUDGE_FILE = pd.read_csv(JUDGE_FILE_PATH, index_col='BuffName')

with open('CharConfig.json', 'r', encoding='utf-8') as file:
    character_config_dict = json.load(file)
config_keys_list = []
for keys in character_config_dict:
    config_keys_list.append(keys)

EXIST_FILE['active'] = EXIST_FILE['active'].map({'FALSE': False, 'TRUE': True})
allbuff_list = EXIST_FILE.index.tolist()  # 把索引列转化为list,注意,此处是所有的!
allbuff_dict = {}  # 用于放所有实例化buff的dict
exist_buff_dict = {}
"""
exist_buff_dict 是当前模拟中,所有可能被激活的buff列表.
不是allbuff,而是从allbuff中挑选了和当前角色以及它们的配装有关的buff,
在后续的循环中,也是由这个dict来充当buff库.这里面装的都是实例化后的buff.

"""
test_weapon_dict ={'艾莲': ['深海访客', 1], '苍角':['含羞恶面', 5], '莱卡恩': ['拘缚者', 1]}


def buff_exist_judge(charname_box, judge_list_set):
    weapon_judge_dict = test_weapon_dict
    for i in allbuff_list:
        row_dict, judge_row_dict = {}, {}  # 把上个循环中用的dict清理干净.
        row_index = i  # 把buff名称提出来
        row_data = EXIST_FILE.loc[i]  # 根据buff名称提取一整行数据,但是这一行数据不包含buff名称
        judge_row_data = JUDGE_FILE.loc[i]
        row_dict = row_data.to_dict()  # 先打包成字典,
        judge_row_dict = judge_row_data.to_dict()
        row_dict['BuffName'] = row_index  # 字典新增一个键值,buff名称.
        judge_row_dict['BuffName'] = row_index
        judged_buff = Buff(row_dict, judge_row_dict)
        if not isinstance(judged_buff, Buff):
            raise ValueError(f'loading_buff中的{judged_buff}元素不是Buff类')
        judged_buff.dy.exist = False
        if judged_buff.ft.bufffrom in judge_list_set:
            if judged_buff.ft.is_weapon:
                for char in charname_box:
                    if judged_buff.ft.bufffrom == (weapon_judge_dict[char][0]) and (judged_buff.ft.refinement == int(weapon_judge_dict[char][1])):
                        judged_buff.ft.exist = True
                        exist_buff_dict[i] = judged_buff
                        break
            else:
                judged_buff.ft.exist = True
                exist_buff_dict[i] = judged_buff
    return exist_buff_dict


"""
exist_buff_dict的格式:buff名:实例化buff
"""
if __name__ == "__main__":      # 测试
    Charname_box = ['艾莲', '苍角', '莱卡恩']
    Judge_list_set = ['艾莲', '深海访客', '极地重金属', '苍角', '含羞恶面', '自由蓝调', '莱卡恩', '拘缚者', '镇星迪斯科']
    exist_buff_dict = buff_exist_judge(Charname_box, Judge_list_set)
    for buffs in exist_buff_dict:
        buff_now = exist_buff_dict[buffs]
        if not isinstance(buff_now, Buff):
            raise TypeError(f'{buff_now}不是Buff类！')
        print(f'{buffs},{buff_now.ft.endjudge}')
