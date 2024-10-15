import pandas as pd
import json
from BuffClass import Buff
from define import EXIST_FILE, JUDGE_FILE

with open('CharConfig.json', 'r', encoding='utf-8') as file:
    character_config_dict = json.load(file)
config_keys_list = []
for keys in character_config_dict:
    config_keys_list.append(keys)

EXIST_FILE['active'] = EXIST_FILE['active'].map({'FALSE': False, 'TRUE': True})
allbuff_list = EXIST_FILE.index.tolist()  # 把索引列转化为list,注意,此处是所有的!
config_check_position_list = [1, 10, 13]  # 角色配置单中,分别记录了角色的名字,武器,4件套.这三个地方的名字将用来判断某些buff是否激活.
allbuff_dict = {}  # 用于放所有实例化buff的dict
exist_buff_dict = {}
"""
exist_buff_dict 是当前模拟中,所有可能被激活的buff列表.
不是allbuff,而是从allbuff中挑选了和当前角色以及它们的配装有关的buff,
在后续的循环中,也是由这个dict来充当buff库.这里面装的都是实例化后的buff.

"""
keybox = ['30词条0+1艾莲', '标准0+1狼哥', '标准6+5苍角']


def buff_exist_judge(charname_box, judge_list_set, key_box):
    weapon_judge_dict = {}
    for key in key_box:
        weapon_judge_dict[character_config_dict[key][1]] = [character_config_dict[key][10], character_config_dict[key][12]]

    for i in allbuff_list:
        row_dict, judge_row_dict = {}, {}  # 把上个循环中用的dict清理干净.
        row_index = i  # 把buff名称提出来
        row_data = EXIST_FILE.loc[i]  # 根据buff名称提取一整行数据,但是这一行数据不包含buff名称
        judge_row_data = JUDGE_FILE.loc[i]
        row_dict = row_data.to_dict()  # 先打包成字典,
        judge_row_dict = judge_row_data.to_dict()
        row_dict['BuffName'] = row_index  # 字典新增一个键值,buff名称.
        judge_row_dict['BuffName'] = row_index
        allbuff_dict[i] = Buff(row_dict, judge_row_dict)  # allbuff_dict 里面装的是所有buff,无论是否exist,都要装进去.
        # 先把所有的buff都实例化,当然是在exist = False的基础上.并全部扔给allbuff_dict.
        judged_buff = allbuff_dict[i]
        if not isinstance(judged_buff, Buff):
            raise ValueError(f'loading_buff中的{judged_buff}元素不是Buff类')
        judged_buff.dy.exist = False

        if judged_buff.ft.bufffrom in judge_list_set:
            if judged_buff.ft.is_weapon:
                for char in charname_box:
                    if judged_buff.ft.bufffrom == weapon_judge_dict[char][0] and judged_buff.ft.refinement == int(
                            weapon_judge_dict[char][1]):
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
