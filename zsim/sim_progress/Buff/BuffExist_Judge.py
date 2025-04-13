import itertools
import json
import copy
import pandas as pd

from sim_progress.Buff.buff_class import Buff
from define import EXIST_FILE_PATH, JUDGE_FILE_PATH, CHARACTER_DATA_PATH

# 加载文件
EXIST_FILE = pd.read_csv(EXIST_FILE_PATH, index_col='BuffName')
JUDGE_FILE = pd.read_csv(JUDGE_FILE_PATH, index_col='BuffName')
CHARACTER_FILE = pd.read_csv(CHARACTER_DATA_PATH, index_col='name')

# 设置初始值和数据预处理
allbuff_list = EXIST_FILE.index.tolist()  # 将索引列转为列表
exist_buff_dict: dict[str, dict[str, Buff]] = {'enemy': {}}  # 初始化敌方buff的字典
buff_name_box: dict[str, list[str]] = {}


# 主函数：判断Buff存在性并更新存在Buff字典
def buff_exist_judge(charname_box, judge_list_set, weapon_dict, cinema_dict):
    exist_buff_dict = {'enemy':{}}
    addition_skill_active_judge_info = {}
    condition_list = ['角色属性-中文', '角色阵营', '角色特性', '支援类型']
    for names in charname_box:
        exist_buff_dict[names] = {}
        sub_info_list = []
        addition_skill_active_judge_info[names] = {}
        addition_skill_active_judge_info[names]['required_condition'] = CHARACTER_FILE.loc[names, '组队被动条件']
        for condition in condition_list:
            sub_info_list.append(CHARACTER_FILE.loc[names, condition])
        addition_skill_active_judge_info[names]['config_info'] = sub_info_list
    # EXPLAIN：以上部分代码的作用是直接通过charname_box中的角色名，
    #  获取character.csv中的对应的组队被动激活判定所需的配置信息，打包列表，并以角色名为键值存入字典。

    total_judge_condition_list = list(itertools.chain.from_iterable(judge_list_set))
    #   把judge_list_set中的内容展开

    name_order_dict = change_name_box(charname_box)
    """
    把根据输入的namebox，分别以“每个角色自身”为主视角（第0号角色）
    创建对应的char_name_box，最后统一打包成name_order_dict。
    举例：
    name_box = [苍角，艾莲，莱卡恩]
    name_order_dict = {
    苍角：[苍角，艾莲，莱卡恩，enemy],
    艾莲：[艾莲，莱卡恩，苍角，enemy],
    莱卡恩：[莱卡恩，苍角，艾莲，enemy]
    }
    """

    # EXPLAIN：将judge_list_set中的信息展开成单层列表，用于buff激活的判定。特别是加给队友类的buff。
    select_buff_dict = preprocess_dataframes(charname_box, EXIST_FILE, JUDGE_FILE, weapon_dict, addition_skill_active_judge_info, total_judge_condition_list, cinema_dict)
    """
    select_buff_dict 是个混杂的字典。里面记录的是“会在此次模拟中被激活的所有buff信息”，但并不包含分类功能。
    比如，艾莲佩戴了冰4，但是苍角、莱卡恩没有，那么冰4相关的所有buff会进入select_buff_dict，
    但是并没有额外的信息来标志“这个冰4buff属于艾莲”这件事，
    需要后续的程序去处理。
    所以，以下代码主要就是负责buff的分类并且实例化这两步。
    """
    for buff_name, buff_info_tuple in select_buff_dict.items():
        buff_from = buff_info_tuple[0]['from']
        adding_code = str(int(buff_info_tuple[0]['add_buff_to'])).zfill(4)
        if buff_from in charname_box:
            # 如果buff来自于角色，那么buff_from就一定指向这个buff的真正来源，也就是buff的拥有者（并非buff的受益者）
            current_name_box = name_order_dict[buff_from]
            selected_characters = [current_name_box[i] for i in range(len(current_name_box)) if adding_code[i] == '1']
            if buff_from not in selected_characters:
                selected_characters.append(buff_from)
            for name in selected_characters:
                initiate_buff(buff_info_tuple, buff_name, exist_buff_dict, name, buff_from)
        elif buff_from == 'enemy':
            """ 
            进入这一分支的所有buff实际上都是环境或是其他原因而强加给enemy的，
            由于buffload函数并不会以“enemy”为主视角来判定buff，
            所有添加给enemy的buff都是在buffload遍历其他角色时产生、或是其他阶段强行添加的，
            所以，此处的buff_orner参数传入并不严格，因为用不到。
            """
            initiate_buff(buff_info_tuple, buff_name, exist_buff_dict, 'enemy', 'enemy')
        elif buff_from in total_judge_condition_list:
            """
            如果buff不属于角色和enemy，那么buff肯定来自装备。
            不管是武器还是驱动盘，都可以通过倒查的方式找到真正的装备者，
            也就是下面的equipment_carrier 变量。
            这个str会被作为buff_orner传入函数。
            """
            for sub_list in judge_list_set:
                if buff_from in [sub_list[1], sub_list[2]]:
                    processor_equipment_buff(adding_code, buff_info_tuple, buff_name, exist_buff_dict, name_order_dict, sub_list)
                elif buff_from == sub_list[3]:
                    if "二件套" in buff_name:
                        processor_equipment_buff(adding_code, buff_info_tuple, buff_name, exist_buff_dict, name_order_dict, sub_list)

    for char_name, sub_buff_dict in exist_buff_dict.items():
        for f_buff in sub_buff_dict.values():
            if not isinstance(f_buff, Buff):
                raise TypeError
            if char_name == 'enemy':
                f_buff.ft.passively_updating = False
            else:
                if f_buff.ft.operator != char_name:
                    f_buff.ft.passively_updating = True
                else:
                    f_buff.ft.passively_updating = False
    # for names, buff_dict in exist_buff_dict.items():
    #     print(names)
    #     for buff_name, buff in buff_dict.items():
    #         print(buff_name, buff.ft.passively_updating, buff.ft.operator, buff.ft.beneficiary)
    return exist_buff_dict


def processor_equipment_buff(adding_code, buff_info_tuple, buff_name, exist_buff_dict, name_order_dict, sub_list):
    equipment_carrier = sub_list[0]
    current_name_box = name_order_dict[equipment_carrier]
    selected_characters = [current_name_box[i] for i in range(len(current_name_box)) if adding_code[i] == '1']
    if equipment_carrier not in selected_characters:
        selected_characters.append(equipment_carrier)
    for name0 in selected_characters:
        initiate_buff(buff_info_tuple, buff_name, exist_buff_dict, name0, equipment_carrier)


def initiate_buff(buff_info_tuple, buff_name, exist_buff_dict, benifiter, buff_orner):
    """
    参数中的benifiter和orner不是一个名字。benifiter是buff的受益者，但并不一定是触发buff的角色。
    而buff_orner是触发buff者，哪怕这个buff是加给别人的，作为触发者，它的exist_buff_dict中也应该保留这个buff，
    这样，在BuffLoad函数对buff_0进行判断时，就可以通过buff.ft.passively_updating参数来避开不必要的判断了。
    """
    dict_1 = copy.deepcopy(buff_info_tuple[0])  # 创建 dict_1 的副本
    dict_2 = copy.deepcopy(buff_info_tuple[1])  # 创建 dict_2 的副本
    dict_1['operator'] = buff_orner
    if benifiter == buff_orner:
        dict_1['passively_updating'] = False
    else:
        dict_1['passively_updating'] = True
    buff_new = Buff(dict_1, dict_2)
    buff_new.ft.beneficiary = benifiter
    exist_buff_dict[benifiter][buff_name] = buff_new


# 数据预处理模块：筛选并打包DataFrame
def preprocess_dataframes(
        name_box: dict,
        exist_file: pd.DataFrame,
        judge_file: pd.DataFrame,
        weapon_dict: dict,
        addition_skill_active_judge_info: dict,
        total_judge_condition_list: list,
        cinema_dict: dict) -> dict:
    """
    根据条件筛选 DataFrame 并打包成字典。

    参数：
        exist_file (pd.DataFrame): 来自激活判断的数据表。
        judge_file (pd.DataFrame): 来自触发判断的数据表。
        filter_conditions (dict): 筛选条件，键为列名，值为筛选值或筛选函数。

    返回：
        dict: 筛选后的结果，格式为 {buff_name: (row_data, judge_row_data)}。
    """
    selected_buffs: dict = {}

    # 遍历 EXIST_FILE，按条件筛选
    for buff_name, row_data in exist_file.iterrows():
        # 判断是否符合所有筛选条件
        buff_from = row_data['from']
        if row_data['is_weapon']:
            for charname in weapon_dict:
                if buff_from == weapon_dict[charname][0] and row_data['refinement'] == weapon_dict[charname][1]:
                    select_buffs(buff_name, judge_file, row_data, selected_buffs)
        elif row_data['is_cinema'] and buff_from in cinema_dict.keys():
            '''处理影画'''
            if row_data['refinement'] <= cinema_dict[buff_from]:
                select_buffs(buff_name, judge_file, row_data, selected_buffs)
        else:
            if buff_from in weapon_dict:
                if row_data['is_additional_ability']:
                    """
                    处理组队被动的模块。步骤如下：
                    1、把激活的两个条件翻译成具体的list，
                    2、将除当前角色（也就是row_data的buff_from）外的另外两个角色的配置列表合并。
                    3、遍历第一步的list，检查其中的条件是否能在另外两个角色的合并列表中找到。
                    4、如果找到，就将buff选入待激活列表，并终止循环。
                    """
                    condition_list_after_trans = addition_skill_info_trans(addition_skill_active_judge_info, buff_from)
                    partner_condition_list = []
                    for other_key in addition_skill_active_judge_info:
                        if other_key != buff_from:
                            partner_condition_list.extend(addition_skill_active_judge_info[other_key]['config_info'])
                    # print(buff_name, condition_list_after_trans, partner_condition_list)
                    for conditions in condition_list_after_trans:
                        if conditions in partner_condition_list:
                            select_buffs(buff_name, judge_file, row_data, selected_buffs)
                            break
                else:
                    if buff_from in name_box:
                        select_buffs(buff_name, judge_file, row_data, selected_buffs)
            elif row_data['from'] == 'enemy':
                select_buffs(buff_name, judge_file, row_data, selected_buffs)
            else:
                if buff_from in total_judge_condition_list:
                    select_buffs(buff_name, judge_file, row_data, selected_buffs)
    return selected_buffs


def addition_skill_info_trans(addition_skill_active_judge_info, buff_from):
    """
    前置函数的初始化会将组队被动的激活条件原封不动地放入字典中（包含|分隔符的字符串）
    此函数是将字符串根据分隔符分割成list，并且根据具体内容进行翻译，
    最后输出的是翻译后的list。
    例如：苍角的组队被动激活条件是‘同属性|同阵营’
    那么翻译过后就会输出：
    ['冰', '对空6课']
    """
    addition_skill_info = addition_skill_active_judge_info[buff_from]
    required_condition_list = addition_skill_info['required_condition'].split('|')
    condition_list_after_trans = []
    for conditions in required_condition_list:
        if conditions == '同阵营':
            condition_list_after_trans.append(addition_skill_info['config_info'][1])
        elif conditions == '同属性':
            condition_list_after_trans.append(addition_skill_info['config_info'][0])
        elif conditions in ['异常', '强攻', '支援', '击破', '防护']:
            condition_list_after_trans.append(conditions)
        elif conditions in ['招架', '回避']:
            condition_list_after_trans.append(conditions)
    return condition_list_after_trans


def select_buffs(buff_name, judge_file, row_data, selected_buffs):
    """
    根据buffname为索引，去dataframe中寻找对应的judge，并且和输入的rowdata打包进入selected buffs
    """
    judge_row_data = judge_file.loc[buff_name]
    row_data['BuffName'] = buff_name
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


if __name__ == '__main__':
    name_box = ['青衣', '丽娜', '零号·安比']
    Judge_list_set = [[name_box[0], '玉壶青冰', '震星迪斯科', '摇摆爵士'],
                      [name_box[1], '好斗的阿炮', '静听嘉音', '如影相随'],
                      [name_box[2], '牺牲洁纯', '如影相随', '啄木鸟电音']]
    char_0 = {'name': name_box[0],
              'weapon': Judge_list_set[0][1], 'weapon_level': 1,
              'equip_set4': Judge_list_set[0][2], 'equip_set2_a': Judge_list_set[0][3],
              'drive4': '暴击率', 'drive5': '电属性伤害', 'drive6': '冲击力%',
              'scATK_percent': 10, 'scCRIT': 20,
              'cinema': 0}
    char_1 = {'name': name_box[1],
              'weapon': Judge_list_set[1][1], 'weapon_level': 5,
              'equip_set4': Judge_list_set[1][2], 'equip_set2_a': Judge_list_set[1][3],
              'drive4': '暴击率%', 'drive5': '穿透率', 'drive6': '能量自动回复%',
              'scATK_percent': 10, 'scCRIT': 20,
              'cinema': 2}
    char_2 = {'name': name_box[2],
              'weapon': Judge_list_set[2][1], 'weapon_level': 1,
              'equip_set4': Judge_list_set[2][2], 'equip_set2_a': Judge_list_set[2][3],
              'drive4': '暴击率', 'drive5': '攻击力%', 'drive6': '攻击力%',
              'scATK_percent': 10, 'scCRIT': 20,
              'cinema': 6}
    weapon_dict = {name_box[0]: [char_0['weapon'], char_0['weapon_level']],
                   name_box[1]: [char_1['weapon'], char_1['weapon_level']],
                   name_box[2]: [char_2['weapon'], char_2['weapon_level']]}
    cinema_dict = {name_box[0]: char_0['cinema'],
                   name_box[1]: char_1['cinema'],
                   name_box[2]: char_2['cinema']}

    exist_buff_dict = buff_exist_judge(name_box, Judge_list_set, weapon_dict, cinema_dict)
    for names, buff_dict in exist_buff_dict.items():
        print(names)
        for buff_name, buff in buff_dict.items():
            print(buff_name, buff.ft.passively_updating, buff.ft.operator)