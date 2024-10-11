import pandas as pd
import json
from BuffClass import Buff
with open('CharConfig.json','r',encoding='utf-8') as file:
    characterconfig_dict = json.load(file)
configkeyslist = []
for keys in characterconfig_dict:
    configkeyslist.append(keys)
judgefilepath = '.\触发判断.csv'
effectfilepath = '.\Buff效果.csv'
exsistfilepath ='.\激活判断.csv'
judgefile = pd.read_csv(judgefilepath, index_col='BuffName')
effectfile = pd.read_csv(effectfilepath, index_col='BuffName')
exsistfile = pd.read_csv(exsistfilepath, index_col='BuffName')
exsistfile['active'] = exsistfile['active'].map({'FALSE': False, 'TRUE': True})
allbuff_list = exsistfile.index.tolist()    # 把索引列转化为list,注意,此处是所有的!
configcheck_positionlist = [1,10,13]        # 角色配置单中,分别记录了角色的名字,武器,4件套.这三个地方的名字将用来判断某些buff是否激活.
allbuff_dict = {}                           # 用于放所有实例化buff的dict
exsistbuff_dict = {}
"""
exsistbuff_dict 是当前模拟中,所有可能被激活的buff列表.
不是allbuff,而是从allbuff中挑选了和当前角色以及它们的配装有关的buff,
在后续的循环中,也是由这个dict来充当buff库.这里面装的都是实例化后的buff.

"""                        
keybox = ['30词条0+1艾莲', '标准0+1狼哥', '标准6+5苍角']

def BuffExsist_Judge(charname_box, judgelist_set, keybox):
    weaponjugde_dict = {}   
    for key in keybox:
        weaponjugde_dict[characterconfig_dict[key][1]] = [characterconfig_dict[key][10],characterconfig_dict[key][12]]
    
    for i in allbuff_list:
        row_dict, judge_rowdict = {}, {}            #把上个循环中用的dict清理干净.
        row_index = i                               #把buff名称提出来
        row_data = exsistfile.loc[i]                #根据buff名称提取一整行数据,但是这一行数据不包含buff名称
        judge_rowdata = judgefile.loc[i]
        row_dict = row_data.to_dict()               #先打包成字典,
        judge_rowdict = judge_rowdata.to_dict()
        row_dict['BuffName'] = row_index            #字典新增一个键值,buff名称.
        judge_rowdict['BuffName'] = row_index
        allbuff_dict[i] = Buff(row_dict, judge_rowdict)     # allbuff_dict 里面装的是所有buff,无论是否exsist,都要装进去.
        # 先把所有的buff都实例化,当然是在exsist = False的基础上.并全部扔给allbuff_dict.
        judgedbuff = allbuff_dict[i]
        judgedbuff.ft.exsist = False
        
        if judgedbuff.ft.bufffrom in judgelist_set:
            if judgedbuff.ft.isweapon:
                for char in charname_box:
                    if judgedbuff.ft.bufffrom == weaponjugde_dict[char][0] and judgedbuff.ft.refinement == int(weaponjugde_dict[char][1]):
                        judgedbuff.ft.exsist = True
                        exsistbuff_dict[i] = judgedbuff
                        break
            else:
                judgedbuff.ft.exsist = True
                exsistbuff_dict[i] = judgedbuff
    return exsistbuff_dict
