import math
from Report import report_to_log
from CharacterClass import Character
classkeydict = {
    'id': 'id',
    'oname': 'OfficialName',
    'sp': 'SpConsumption',
    'spr': 'SpRecovery_hit',
    'fev': 'FeverRecovery',
    'eaa': 'ElementAbnormalAccumlation',
    'st': 'SkillType',
    'tbl': 'TriggerBuffLevel',
    'et': 'ElementType',
    'tc': 'TimeCost',
    'hn': 'HitNumber',
    'da': 'DmgRelated_Attributes',
    'sa': 'StunRelated_Attributes'
}

Buffeffect_index = [
    "BuffName", "eventid", "charactername", "actionname", 
    "f_hp", "f_atk", "f_defs", "f_bs", "f_cr", "f_cd", "f_eap", "f_em", "f_pr", "f_pd", "f_spr", "f_spgr", "f_spm", "f_phy","f_fir", "f_ice", "f_ele", "f_eth",
    "o_hp", "o_atk", "o_defs", "o_bs", "o_cr", "o_cd","o_eap", "o_em", "o_pr", "o_pd", "o_spr", "o_spgr", "o_spm", "o_phy", "o_fir", "o_ice", "o_ele", "o_eth",
    "PhyBonus", "FireBonus", "IceBonus", "EleBonus", "EthBonus", "AttackType",
    "NormalAttack", "SpecialSkill", "ExSpecial", "Dashattack", "Avoidattack", "QTE", "Q",
    "BHaid", "Parryaid", "Assaultaid", "ElementalStatus", "ALLDMG", "Defincrease", "Defdecrease",
    "Deffix", "Pendelta", "Pendelta_Ratio", "Element_reduce", "Element_penetrate", "PhyRes",
    "FireRes", "IceRes", "EleRes", "EthRes", "AllRes", "Chance_to_be_crit", "Damage_from_crit",
    "Dmgtaken_Increase", "Dmgtaken_Decrease", "StunDamage_TakeRatio", "StunDamage_TakeRatio_Delta",
    "Special_Multiplication_Zone"
    ]   
    # 这个index列表里面装的是乘区类型中所有的项目,也是buff效果作用的范围.
    # 这个列表中的内容:在Buff效果.csv 中作为索引存在;而在 Event父类中,它们又包含了 info子类的部分内容 和 multiplication子类的全部内容,
    # 在文件中,这个list被用在最后的buffchagne()函数中,作为中转字典的keylist存在
    # 在重构本程序的过程中,我思考过是否要把这个巨大的indexlist按照乘区划分拆成若干,这意味着Event中的Multi子类或许可以独立出来成为一个单独的父类存在.
    # 这样做的好处是:庞大复杂的Multi可以不用蜗居在Event下,结构更加清晰.但是坏处就是,Event和Multi必须1对1实例化,否则容易出现多个动作共用同一份乘区实例的情况,就很容易发生错误NTR(bushi

class Buff:
    def __init__(self, config, judgeconfig):
        self.ft = self.Buff_Feature(config) 
        self.dy = self.Buff_Dynamic()
        self.sjc = self.Buff_SimpleJudge_Condition(judgeconfig)
        self.logic = self.Buff_logic()

    class Buff_Feature:
        def __init__(self, config):
            self.simple_start_logic = config['simple_start_logic']
            self.simple_end_logic = config['simple_end_logic']
            self.simple_effect = config['simple_effect']
            self.index = config['BuffName']                       # buff的英文名,也是buff的索引
            self.isweapon = config['isweapon']                    # buff是否是武器特效
            self.refinement = config['refinement']                # 武器特效的精炼等级
            self.bufffrom = config['from']                        # buff的来源,可以是角色名,也可以是其他,这个字段用来和配置文件比对,比对成功则证明这个buff是可以触发的;
            self.name = config['name']                            # buff的中文名字,包括一些buff效果的拆分,这里的中文名写的会比较细
            self.exsist = config['exsist']                        # buff是否参与了计算,即是否允许被激活
            self.durationtype = config['durationtype']            # buff的持续时间类型,如果是True,就是有持续时间的,如果是False,就没有持续时间类型,属于瞬时buff.
            self.maxduration = config['maxduration']              # buff最大持续时间
            self.maxcount = config['maxcount']                    # buff允许被叠加的最大层数
            self.step = config['incrementalstep']                 # buff的自增步长,也可以理解为叠层事件发生时的叠层效率.
            self.prejudge = config['prejudge']                    # buff的判定类型,True是提前判定类型,即未命中先有buff;False是命中后类型,当前动作不受影响.
            self.fresh = config['freshtype']                      # buff的刷新类型,True是刷新层数时,刷新时间,False是刷新层数是,不影响时间.
            self.alltime = config['alltime']                      # buff的永远生效类型,True是无条件永远生效,False是有条件
            self.hitincrease = config['hitincrease']              # buff的层数增长类型,True就增长层数 = 命中次数,而False是增长层数为固定值,取决于step数据;
            self.cd  = config['increaseCD']                       # buff的叠层内置CD

    class Buff_Dynamic:
        def __init__(self):
            self.exsist = False         # buff是否参与了计算,即是否允许被激活
            self.active = False         # buff当前的激活状态
            self.count = 0              # buff当前层数
            self.ready = True           # buff的可叠层状态,如果是True,就意味着是内置CD结束了,可以叠层,如果不是True,就不能叠层.
            self.startticks = 0         # buff上一次触发的时间(tick)
            self.endticks = 0           # buff计划课中,buff的结束时间
            self.lastend = 0            # buff上一次结束的时间
            self.activetimes = 0        # buff迄今为止激活过的次数
            self.lastduration = 0       # buff上一次的持续时间
            self.endtimes = 0           # buff结束过的次数
    
    class Buff_logic:
        def __init__(self):
            self.xstart = None
            self.xeffect = None
            self.xend = None
            
    class Buff_SimpleJudge_Condition:
        def __init__(self, judgeconfig):
            self.id = judgeconfig['id']
            self.oname = judgeconfig['OfficialName']
            self.sp = judgeconfig['SpConsumption']
            self.spr = judgeconfig['SpRecovery_hit']
            self.fev = judgeconfig['FeverRecovery']
            self.eaa = judgeconfig['ElementAbnormalAccumlation']
            self.st = judgeconfig['SkillType']
            self.tbl = judgeconfig['TriggerBuffLevel']
            self.et = judgeconfig['ElementType']
            self.tc = judgeconfig['TimeCost']
            self.hn = judgeconfig['HitNumber']
            self.da = judgeconfig['DmgRelated_Attributes']
            self.sa = judgeconfig['StunRelated_Attributes']

    def readyjudge(self, timenow):
        """
        用来判断内置CD是否就绪
        """
        if not self.dy.ready:
            if timenow - self.dy.startticks >= self.ft.cd:
                self.dy.ready = True 

    def end(self, timenow):
        """
        用来执行buff的结束
        """
        self.dy.active = False
        self.dy.count = 0
        self.dy.lastend = timenow
        self.dy.endtimes += 1
        self.dy.lastduration = max(self.dy.lastend - self.dy.startticks, 0)
        report_to_log(f'当前ticks是{timenow};这是一个Buff类事件;{self.ft.name}结束了;这是它第{self.dy.endtimes}次结束;本次激活持续了{self.dy.lastduration}ticks')

    def timeupdate(self, timecost, timenow):
        """
        在Buff确定要触发的时候,更新buff的starttime,endtime等一系列参数;
        这里不包含内置Cd的判定,默认内置CD已经判定通过.
        注意事项:
        1,这个函数只修改 startticks 和 endticks两个数值
        由于在本函数的开头,需要对buff的当前active进行判断,以筛选出那些"尚未结束但又触发"的buff,
        所以,关于buff.dy.active的修改应在timeupdate函数生效后进行.故不在本函数内修改active.
        2,关于freshtype是False的那些buff,也就是更新但不刷新时间的buff,它们在非重复触发的状态下,和普通buff是一致的.
        所以只需要找出那些重复触发的此类buff,并不对时间做任何修改即可;
        3,对于持续时间为0的瞬时buff,应将其看做持续时间为招式持续时间的有时长的buff一并对待.
        """      
        if not self.ft.fresh:
            if self.dy.active:
                return
        if self.ft.maxduration == 0:
            self.dy.endticks = timenow + timecost
            self.dy.startticks = timenow 
        if self.ft.prejudge:
            self.dy.startticks = timenow
            self.dy.endticks = timenow + self.ft.maxduration
        else:
            self.dy.startticks = timenow + timecost
            self.dy.endticks = timenow + timecost + self.ft.maxduration

    def countupdate(self, be_hitted: bool):
        """
        如果 self.ft.hitincrease 为 False,则无需关心 be_hitted 的值,直接执行 self.dy.count 的增加操作.
        如果 self.ft.hitincrease 为 True,则只在 be_hitted 为 True 时增加 self.dy.count.
        """
        if not self.ft.hitincrease or be_hitted:
            self.dy.count = min(self.dy.count + self.ft.step, self.ft.maxcount)

    def buff_add(self, timenow, timecost, be_hitted:bool, loading_buff:list, DYNAMIC_BUFF_LIST:list):
        """
        用来添加buff的总函数。它能新增buff到DYNAMIC_BUFF_LIST中,
        注意，该函数不包含判断逻辑，应在执行完buff是否要激活的判断后，再执行这个函数。
        它首先会判断buff内置CD是否就绪，内置Cd没转完的不执行激活操作；
        然后会判断buff的simple_start_logic类型，如果是true，则进行简单更新，运行time和count的 update函数
        最后，无论是什么逻辑，都会更新buff的active、activetimes，同时将内置Cd刷新，重置为False状态
        最后对DYNAMIC_BUFF_LIST进行添加操作；
        
        """
        for buff in loading_buff:
            if not isinstance(buff, Buff):
                print(f'loading_buff中的{buff}元素不是Buff类')
                return
            if not buff.readyjudge(timenow):
                continue
            if buff.ft.simple_start_logic:
                    buff.timeupdate(timenow, timecost)
                    buff.countupdate(be_hitted)
            else:
                buff.logic.xstart
            buff.dy.active = True
            buff.dy.activetimes += 1
            buff.dy.ready = False
            DYNAMIC_BUFF_LIST.append(buff)
            report_to_log(f'当前ticks是{timenow};这是一个Buff类事件;{self.ft.name}触发了;这是它第{self.dy.endtimes}次触发;本次激活预计到第{self.dy.lastduration}ticks结束')
