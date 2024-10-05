import xlwings as xw
from Parameter import get_parameter
from Change_Float import convert_to_float
from CharacterClass import Character
import json

wb = xw.Book('F:\GithubProject\ZZZ_Calculator\绝区零数据库.xlsx')
with open('CharConfig.json','r',encoding='utf-8') as file:
    characterconfig_dict = json.load(file)
characterconfig_range = ['D3','D2','D4','H38',
                         'D6','C38','D38','E38','F38','G38',
                         'F2','F3','F4','D9','E9','F9','G9',
                         'D11', 'E11', 'F11', 'G11','H11','I11',
                         'J1','M2','M3','M4','M5','M6','M7','M8','M9','M10','M11']#和配装方案对应，记录的是每一位数值填写到哪个单元格里面去
keys = ['id', 'name', 'level', 'talent', 
    'unique_skill', 'normal_attack', 'dash_skill', 'support_skill', 'special_skill', 'qte_skill',
    'weapon', 'weapon_level', 'refinement', 'equipment_set4', 'equipment_set2_a', 'equipment_set2_b', 'equipment_set2_c',
    'position1', 'position2', 'position3', 'position4', 'position5', 'position6',
    'sum', 'hp', 'attack', 'defense', 'hpper', 'atkper', 'defper', 'cr', 'cd', 'elementmystery', 'pendelta',]
skill_stat_keys = ['id', 'Name', 'OfficialName', 
                   'DmgRatio', 'StunRatio', 'SpConsumption', 
                   'SpRecovery_hit', 'FeverRecovery', 
                   'ElementAbnormalAccumlation', 'SkillType', 'TriggerBuffLevel', 'ElementType', 
                   'TimeCost', 'HitNumber', 
                   'DmgRelated_Attributes', 'StunRelated_Attributes']
configcheck_positionlist = [1, 10, 13] #角色配置单中，分别记录了角色的名字，武器，4件套。这三个地方的名字将用来判断某些buff是否激活。
calculate_box = {}
statementkeys = ['hp', 'atk', 'defs', 'bs', 'cr', 'cd', 'eap', 'em', 'pr', 'pd', 'spr', 'spgr', 'spm', 'phy', 'fir', 'ice', 'ele', 'eth']
keybox = []
characterbox_now = [None, None, None]
sheet_basic = wb.sheets['配装&面板']
statementbasic_box = {}
statementBonus_box = {}
statementoutside_box = {}
activcharacter_allskilldict = {}
activ_characterbox = [None, None, None]


def character_set():        #角色基础配置更新
    while True:
        characternumber = input("请输入参与计算的角色数量：")       #输入角色数量
        try:
            characternumber = int(characternumber)
            if characternumber >3 or characternumber<1:
                print("输入错误，角色数量最小为1，最大为3，请重新输入。")
                continue
            else:
                print(f"当前参与计算的角色数量为：{characternumber}")
                break
        except ValueError:
            print("请输入有效的整数。")
            continue
    listnumber = len(characterconfig_dict)
    keys_list = list(characterconfig_dict.keys())
    print('现有配装方案如下，请选择：')
    for i in range(listnumber):
        print(i+1,'、',keys_list[i])

    for k in range(characternumber):
         while True:
            setnumber = get_parameter(f'请输入需要导入的第{k + 1}位角色的配装方案序号：', lambda x: x.isdigit() and 0 < int(x) <= listnumber)       #输入需要的配装方案代号
            setnumber = int(setnumber)
            if setnumber <= listnumber:
                selected_key = keys_list[setnumber - 1]


                print(f"已选择的配装方案为：{selected_key}")        # 在这里可以根据 selected_key 进行进一步操作，例如更新角色的配置，
                                                                  # 这个变量里面记录了当前循环的dict里面的对应位置的键值，
                                                                  #=====>比如“标准30词条0+1艾莲”<=====
                
                keybox.append(selected_key)                       #把每次用于检索的selectkey 都放到keybox列表中，
                characterconfig_now = characterconfig_dict[selected_key]        #把总配装方案dict中的第k个键对应的值（是一个列表）拿出来，放到这个now变量里面，
                characterbox_now[k] = characterconfig_dict[selected_key][1] #按顺序记录激活的角色

                #config_list.append(characterconfig_now)           #把每次从配置列表里面取出来的select_key对应的键值（是一个{……}）放到外面的config_list里面//这一行暂时弃置
            
                for i in range(34): 
                    sheet_basic.range(characterconfig_range[i]).value = characterconfig_now[i]
                    #把now变量里面的内容，填写到range列表中记录的一个个位置里，
                    
                characterconfig_now = [convert_to_float(item) for item in characterconfig_now]      #把里面能转成数值的项目，转化成数值

                configdict = dict(zip(keys,characterconfig_now))        #角色配置信息提炼出来的字典，

                calculate_box[selected_key] = configdict                #信息汇总到计算用的dict中,里面的内容是========>{配装方案名:{id:xxx, name:xxx, ......}}


                characterbase_statlist = sheet_basic.range('C20:T20').value                 #临时用来存储角色属性的list
                characterbase_statdict = dict(zip(statementkeys,characterbase_statlist))     #把list里面的数值，和statementkeys里面的键值一一对应，装入dict里面
                statementbasic_box[selected_key] = characterbase_statdict                    #在总字典中录入信息，即{配装方案名字：{hp:xxx, atk:xxx ……}}
                bonuslist = []      #令一个空list，用来2合1

                fixbonus = sheet_basic.range('C31:T31').value               #令一个空list，用来装固定加成
                percentbonus = sheet_basic.range('C32:T32').value           #令一个空list，用来装百分比加成
                statementoutside_lsit = sheet_basic.range('C33:T33').value   #令一个空list，用来装角色站街面板
                for i in range(len(statementkeys)):
                    bonuslist.append([fixbonus[i],percentbonus[i]])
                bonusdict = dict(zip(statementkeys,bonuslist))        #另一个空的dict，用来和bonuslist进行zip
                statementBonus_box[selected_key] = bonusdict         #封包到statementBonus里面去，即{配装方案名字：{hp:[a,b], atk:[a,b], ……}}
                statementoutside_dict = dict(zip(statementkeys, statementoutside_lsit))    #打包成字典，{hp:xxx, atk:xxx, ……}
                statementoutside_box[selected_key] = statementoutside_dict                #进一步打包成{配装方案名:{hp:xxx, atk:xxx, ……}}
                #接下去的内容，是要准备为角色录入技能数据。
                #首先是从表里面拿出来，我们从sheet_basic  也就是“配装&面板”表中，获取A42单元格的内容，那里，记录着取值范围，这个取值范围的值，本来是记录了有多少个技能被调用出来了，
                #而这个值，直接决定了查阅数值的循环次数。

                #第一步，新建一个空的字典，一会儿用来装拿出来的数据。
                #当然，如果我们是第二次来到这里，那么就应该是清空旧字典中的内容了，应新的空字典去装新的角色。
                skillcopydata = {}

                #把A42的那个取值范围拿出来，并且转化为int
                count = sheet_basic.range('A40').value
                count = int(count)
                print(f'本次录入的角色技能共有{count}个！')


                #开始循环。
                for i in range(count):
                    
                    #起始行数
                    rowstart = 42

                    #终止行数，第1次循环，那就是42，第2次循环，那就是43，以此类推，
                    rownow = rowstart + i

                    #用来装技能数据的字典，新建一个键值，键值的内容是'A'列中记录的技能名，并且对这个键值进行赋值，赋值的内容是一个zip打包过后的新字典
                        #首先，把当前这一行的B~Q列的内容抄下来，
                        #用zip语法，和早在前面新建好的列表  skill_stat_keys 进行一一对应的打包，变成了一个记录了单一技能信息的字典，比如
                        #{普攻第一段：{攻击倍率：xxxxx, 失衡倍率：xxxxx, ……}}
                        #在当前循环结束后，我们应该会得到一个大字典，其中记录了这个角色的所有技能信息，每个技能都有自己的各种倍率、回能信息，
                    
                    
                    skillcopydata[sheet_basic.range(f'A{rownow}').value] = dict(zip(skill_stat_keys,sheet_basic.range(f'B{rownow}:Q{rownow}').value))


                    #print(f'加载第{i+1}个技能： ',skillcopydata[sheet_basic.range(f'A{rownow}').value]['id'])   #实时通报加载进度
                #在循环结束后，单个角色的信息录入来到了尾声，我们需要把刚才循环20~40次才得到的大型技能信息表，传递到循环外面，也就是用最终字典activcharacter_allskilldict来装他们，键值就是角色名
                #于是，在该角色信息录入的末尾，我们在最终字典中加入了如下信息：
                #{角色配装方案名：{技能信息1，技能信息2，技能信息3，}}
                activcharacter_allskilldict[selected_key] = skillcopydata
                break
            else:
                print("输入不符合要求，请重新输入。")
                continue
        
    #然后把字典中的每个键值对应的元素，传递到character类
    for i in range(characternumber):        
        activ_characterbox[i] = Character(calculate_box[keybox[i]],
                                          statementbasic_box[keybox[i]],
                                          statementBonus_box[keybox[i]],
                                          statementoutside_box[keybox[i]],
                                          activcharacter_allskilldict[keybox[i]])
    wb.save
    #wb_t.save
    print(f'现已激活的角色列表为：{characterbox_now}')
    return characternumber, characterbox_now, activ_characterbox
