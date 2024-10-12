from BuffClass import Buff
from CharSet_new import Character
def buff_load(CHARACTER_ORDER_DICT:dict, exsistbuff_dict:dict, action, used_buffname_box:list):
    """
    这是buff修改三部曲的第二步,也是最核心的一个步骤.\n
    该函数有以下几个功能:\n
        1,判断当前动作是否会触发buff\n
        2,如果buff触发,则将buff添加到LOADING_BUFF_DICT中,这部分需要和受益者进行打包.\n
        3,受益者是激活判断.csv中的一个字段,叫做add_buff_to,它由2进制转译为10进制并记录,\n
            在buff实例化的时候,这个字段会一起被实例化,并且可以用buff.ft.add_buff_to调用,\n
            具体的翻译表如下:\n
    给自己____下一个__上一个_____二进制_______十进制______含义\n
    0__________0________0___________000__________0____________无\n
    0__________0________1___________001__________1____________只给上一个\n
    0__________1________0___________010__________2____________只给下一个\n
    0__________1________1___________011__________3____________给所有后台角色\n
    1__________0________0___________100__________4____________只给自己\n
    1__________0________1___________101__________5____________给自己和上一个\n
    1__________1________0___________110__________6____________给自己和下一个\n
    1__________1________1___________111__________7____________给全队\n
        4,程序运行时,需要传入的几个参数中,character_order_dict中记录了当前tick中角色的前后台关系,\n
            该DICT包含了三个key,分别是:on_field, next 和 previous三个,分别代表当前在场,下一位和上一位,\n
    """
    LOADING_BUFF_DICT = {}
    for _ in CHARACTER_ORDER_DICT:
        LOADING_BUFF_DICT[CHARACTER_ORDER_DICT[_]] = []
    # 初始化LOADING_BUFF_DICT,清空
    for item in exsistbuff_dict:
        buff = exsistbuff_dict[item]
        if not isinstance(buff, Buff):
            raise ValueError(f'在buff_load环节发现{exsistbuff_dict}中的{buff}不是Buff类的实例')
        if buff.dy.index in used_buffname_box:
            
        binary_str = f'{int(buff.ft.add_buff_to):03b}'