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
    total_judge_condition_list = list(itertools.chain.from_iterable(judge_list_set))

    name_order_dict = change_name_box(charname_box)
    for buff_name, buffs in selected_buffs.items():
        if not isinstance(buffs, Buff):
            raise ValueError(f'加载的 {buff_name} 不是 Buff 类的实例')
        if buffs.ft.bufffrom != 'enemy':
            char_name = buffs.ft.bufffrom
            order_list = name_order_dict[char_name]




    #
    # for k, charname in enumerate(charname_box):
    #     sub_exist_buff_dict = {}
    #     for buff_name in allbuff_list:
    #         row_data = EXIST_FILE.loc[buff_name]
    #         judge_row_data = JUDGE_FILE.loc[buff_name]
    #         judged_buff = instantiate_buff(row_data, judge_row_data, buff_name)
    #
    #         if not isinstance(judged_buff, Buff):
    #             raise ValueError(f'加载的 {buff_name} 不是 Buff 类的实例')
    #
    #         judged_buff.dy.exist = False
    #         buff_from = judged_buff.ft.bufffrom
    #         if (buff_from in judge_list_set[k]) or ((buff_from in total_judge_condition_list) and (judged_buff.ft.add_buff_to != 1000)) or (buff_from == 'enemy'):
    #             # 虽然当前正在处理的是角色A的buff，但是如果角色B的buff也能加给A（此时该buff的 add_buff_to的值就不是1000了）
    #             #  那么buff也会被列入A角色的exist_buff_dict中。
    #             process_buff(judged_buff, charname, weapon_dict, sub_exist_buff_dict, exist_debuff_dict)
    #     exist_buff_dict[charname] = sub_exist_buff_dict
    # exist_buff_dict['enemy'] = exist_debuff_dict
    # # print([buff.ft.index for buff in exist_buff_dict['艾莲'].values()])
    # return exist_buff_dict




# TODO：组队被动检测
# TODO：影画buff的录入与检测


# 数据预处理模块：筛选并打包DataFrame
def preprocess_dataframes(exist_file: pd.DataFrame, judge_file: pd.DataFrame, weapon_dict: dict) -> dict:
    """
    根据条件筛选 DataFrame 并打包成字典。

    参数：
        exist_file (pd.DataFrame): 来自激活判断的数据表。
        judge_file (pd.DataFrame): 来自触发判断的数据表。
        filter_conditions (dict): 筛选条件，键为列名，值为筛选值或筛选函数。

    返回：
        dict: 筛选后的结果，格式为 {buff_name: (row_data, judge_row_data)}。
    """
    selected_buffs = {}

    # 遍历 EXIST_FILE，按条件筛选
    for buff_name, row_data in exist_file.iterrows():
        # 判断是否符合所有筛选条件
        if row_data['is_weapon']:
            for charname in weapon_dict:
                if row_data['from'] == weapon_dict[charname][0] and row_data['refinement'] == weapon_dict[charname][1]:
                    select_buffs(buff_name, judge_file, row_data, selected_buffs)
        else:
            if row_data['from'] in weapon_dict:
                if row_data['is_additional_ability']:
                    pass
                else:
                    select_buffs(buff_name, judge_file, row_data, selected_buffs)
            if row_data['from'] == 'enemy':
                select_buffs(buff_name, judge_file, row_data, selected_buffs)

        # 取对应的 judge_file 行并保存结果
        select_buffs(buff_name, judge_file, row_data, selected_buffs)

    return selected_buffs


def select_buffs(buff_name, judge_file, row_data, selected_buffs):
    """
    根据buffname为索引，去dataframe中寻找对应的judge，并且和输入的rowdata打包进入selected buffs
    """
    judge_row_data = judge_file.loc[buff_name]
    selected_buffs[buff_name] = (row_data, judge_row_data)


def change_name_box(name_box: list):
    """
    生成每个角色对应的namebox列表，以自己作为第0位角色。
    """
    output_name_dict = {}
    for i in range(len(name_box)):
        new_name_box = name_box[i:] + name_box[:i]
        output_name_dict[name_box[i]] = new_name_box + ['enemy']
    return output_name_dict


