from 计算 import Buff
import pandas as pd
from 计算 import characterconfig_dict, keybox, exsistfile, configcheck_positionlist, allbuff_list#, characterbox_now

characterbox_now = ['艾莲', '莱卡恩', '苍角']
#确认exsistfile文件中，exsist列是否是布尔值，如果不是，则转换为布尔值。
if 'exsist' not in exsistfile.columns:
    exsistfile['exsist'] = False
else:
    exsistfile['exsist'] = exsistfile['exsist'].astype(bool)


allbuff_dict = {}
allbuff_dict_char = {}
def Charbufflist(characterbox_now):

    for charnumber in range(len(characterbox_now)):    #这是为了将参与计算的每个角色的buff列表都单独放开，
        charbuff_minor = {}
        #创建检查用的配置单
        testlist = []
        for a in configcheck_positionlist:
            testlist.append(characterconfig_dict[keybox[charnumber]][a])

        #检查激活状态的循环，如果buff的from，在配置单中，那么就修改exsist为True，否则就为False
        for i in allbuff_list:
            row_dict = {}           #把上个循环中用的dict清理干净。
            row_index = i           #把buff名称提出来

            row_data = exsistfile.loc[i]                #根据buff名称提取一整行数据，但是这一行数据不包含buff名称
            row_dict = row_data.to_dict()               #先打包成字典，
            row_dict['BuffName'] = row_index            #字典新增一个键值，buff名称。
            charbuff_minor[i] = Buff(row_dict)       #对allbuffdict中的每一个buff的键值进行Buff类的实例化

            #对exsist属性进行初始化
            if exsistfile.loc[i, 'from'] in testlist:
                #exsistfile.loc[i, 'exsist'] = True #废弃代码1
                charbuff_minor[i].exsist = True
            else:
                #exsistfile.loc[i, 'exsist'] = False #废弃代码1
                charbuff_minor[i].exsist = False
            # exsistfile.to_csv(exsistfilepath, index = True) #废弃代码1
        allbuff_dict_char[characterbox_now[charnumber]] = charbuff_minor
    
    return allbuff_dict_char


