import itertools
import json

import pandas as pd

from Buff.buff_class import Buff
from define import EXIST_FILE_PATH, JUDGE_FILE_PATH

# 加载文件
EXIST_FILE = pd.read_csv(EXIST_FILE_PATH, index_col='BuffName')
JUDGE_FILE = pd.read_csv(JUDGE_FILE_PATH, index_col='BuffName')

with open('./CharConfig.json', 'r', encoding='utf-8') as file:
    character_config_dict = json.load(file)

# 设置初始值和数据预处理
config_keys_list = list(character_config_dict.keys())
allbuff_list = EXIST_FILE.index.tolist()  # 将索引列转为列表
exist_buff_dict = {'enemy': {}}  # 初始化敌方buff的字典


# 提取所有Buff并实例化的函数
def instantiate_buff(row_data, judge_row_data, buff_name):
    row_dict = row_data.to_dict()
    judge_row_dict = judge_row_data.to_dict()
    row_dict['BuffName'] = buff_name
    judge_row_dict['BuffName'] = buff_name
    return Buff(row_dict, judge_row_dict)


def process_buff(judged_buff, charname, weapon_dict, sub_exist_buff_dict, exist_debuff_dict):
    # 判断武器相关Buff
    if judged_buff.ft.is_weapon:
        weapon_name, refinement = weapon_dict[charname]
        if (judged_buff.ft.bufffrom == weapon_name) and (judged_buff.ft.refinement == int(refinement)):
            # 如果武器的名字和精炼等级都对上了，那么就通过。
            judged_buff.ft.exist = True
            if judged_buff.ft.is_debuff:
                exist_debuff_dict[judged_buff.ft.index] = judged_buff
            else:
                sub_exist_buff_dict[judged_buff.ft.index] = judged_buff
    else:
        judged_buff.ft.exist = True
        if judged_buff.ft.is_debuff:
            exist_debuff_dict[judged_buff.ft.index] = judged_buff
        else:
            sub_exist_buff_dict[judged_buff.ft.index] = judged_buff


# 主函数：判断Buff存在性并更新存在Buff字典
def buff_exist_judge(charname_box, judge_list_set, weapon_dict):
    exist_debuff_dict = {}
    total_judge_condition_list = list(itertools.chain.from_iterable(judge_list_set))
    for k, charname in enumerate(charname_box):
        sub_exist_buff_dict = {}
        for buff_name in allbuff_list:
            row_data = EXIST_FILE.loc[buff_name]
            judge_row_data = JUDGE_FILE.loc[buff_name]
            judged_buff = instantiate_buff(row_data, judge_row_data, buff_name)

            if not isinstance(judged_buff, Buff):
                raise ValueError(f'加载的 {buff_name} 不是 Buff 类的实例')

            judged_buff.dy.exist = False
            buff_from = judged_buff.ft.bufffrom
            if (buff_from in judge_list_set[k]) or ((buff_from in total_judge_condition_list) and (judged_buff.ft.add_buff_to != 1000)) or (buff_from == 'enemy'):
                # 虽然当前正在处理的是角色A的buff，但是如果角色B的buff也能加给A（此时该buff的 add_buff_to的值就不是1000了）
                #  那么buff也会被列入A角色的exist_buff_dict中。
                process_buff(judged_buff, charname, weapon_dict, sub_exist_buff_dict, exist_debuff_dict)

        exist_buff_dict[charname] = sub_exist_buff_dict

    exist_buff_dict['enemy'] = exist_debuff_dict
    return exist_buff_dict


# 测试代码
if __name__ == "__main__":
    Charname_box = ['艾莲', '苍角', '莱卡恩']
    Judge_list_set = [['艾莲', '深海访客', '极地重金属'], ['苍角', '含羞恶面', '自由蓝调'],
                      ['莱卡恩', '拘缚者', '镇星迪斯科']]
    weapon_dict = {'艾莲': ['深海访客', 1], '苍角': ['含羞恶面', 5], '莱卡恩': ['拘缚者', 1]}

    exist_buff_dict = buff_exist_judge(Charname_box, Judge_list_set, weapon_dict)
    for name, sub_dict in exist_buff_dict.items():
        print(name)
        for _ in sub_dict.values():
            print(_.ft.index)

    # for buffs in exist_buff_dict['enemy']:
    #     buff_now = exist_buff_dict['enemy'][buffs]
    #     if not isinstance(buff_now, Buff):
    #         raise TypeError(f'{buff_now}不是Buff类！')
    #     print(f'{buffs}, {buff_now.ft.endjudge}')
