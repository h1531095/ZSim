import math
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
class Buff:
    def __init__(self, config, character, enemy, mult, buffjson, effectdict, judgeconfig):
        self.ft = self.Buff_Feature(config) 
        self.dy = self.Buff_Dynamic()
        self.logic = self.Buff_Logic(buffjson, config, character, enemy)
        self.effect = self.Buff_Effect(buffjson, config, character, enemy, mult, self.ft, effectdict)
        self.sjc = self.Buff_SimpleJudge_Condition(judgeconfig)

    class Buff_Feature:
        def __init__(self, config):
            self.simple_logic = config['simple_logic']
            self.simple_effect = config['simple_effect']
            self.index = config['BuffIndex']                      # buff的英文名，也是buff的索引
            self.bufffrom = config['from']                        # buff的来源，可以是角色名，也可以是其他，这个字段用来和配置文件比对，比对成功则证明这个buff是可以触发的；
            self.name = config['name']                            # buff的中文名字，包括一些buff效果的拆分，这里的中文名写的会比较细
            self.exsist = config['exsist']                        # buff是否参与了计算，即是否允许被激活
            self.durationtype = config['durationtype']            # buff的持续时间类型，如果是True，就是有持续时间的，如果是False，就没有持续时间类型，属于瞬时buff。
            self.maxduration = config['maxduration']              # buff最大持续时间
            self.maxcount = config['maxcount']                    # buff允许被叠加的最大层数
            self.step = config['incrementalstep']                 # buff的自增步长，也可以理解为叠层事件发生时的叠层效率。
            self.prejudge = config['prejudge']                    # buff的判定类型，True是提前判定类型，即未命中先有buff；False是命中后类型，当前动作不受影响。
            self.fresh = config['freshtype']                      # buff的刷新类型，True是刷新层数时，刷新时间，False是刷新层数是，不影响时间。
            self.alltime = config['alltime']                      # buff的永远生效类型，True是无条件永远生效，False是有条件
            self.hitincrease = config['hitincrease']              # buff的层数增长类型，True就增长层数 = 命中次数，而False是增长层数为固定值，取决于step数据；
            self.cd  = config['increaseCD']                       # buff的叠层内置CD

        def getlogic(self):
            return self.simple_logic

        def geteffect(self):
            return self.simple_effect

    class Buff_Dynamic:
        def __init__(self):
            self.exsist = False         # buff是否参与了计算，即是否允许被激活
            self.active = False         # buff当前的激活状态
            self.duration = 0           # buff当前剩余时间
            self.count = 0              # buff当前层数
            self.ready = True           # buff的可叠层状态，如果是True，就意味着是内置CD结束了，可以叠层，如果不是True，就不能叠层。
            self.last = 0               # buff上一次触发的时间

    class Buff_Logic:
        def __init__(self, buffjson, config, character, enemy):
            self.xlogic = buffjson['logic']

    class Buff_Effect:
        def __init__(self, buffjson, config, character, enemy, mult, ft, effectdict):
            self.eff = buffjson['effect']
            self.effdict = effectdict
            self.ft = ft
            self.elogic = self.ft.getlogic()

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

    def readyjudge(self, timenow):                                  # 用来判断叠层内置CD是否就绪的函数
        if not self.dy.ready:
            if timenow - self.dy.last >= self.ft.cd:
                self.dy.ready = True 

    def end(self):
        self.dy.duration = 0
        self.dy.active = False
        self.dy.count = 0

    def re_time(self, timecost):            # buff刷新或刚触发时的时间计算函数，该函数在fresh属性是True时生效，即buff刷新，持续时间也刷新。
        if self.ft.prejudge:
            self.dy.duration = max(self.ft.maxduration - timecost, 0)
        else:
            self.dy.duration = self.ft.maxduration

    def re_count(self, hitnumber, timecost):
        # buff刷新或刚触发的层数计算函数
        if self.ft.hitincrease:
            self.dy.count = min(math.ceil(timecost/max(timecost/hitnumber, self.ft.cd)) * self.ft.step, self.ft.maxcount) 
        else:
            self.dy.count = min(self.ft.step, self.ft.maxcount)

    def timeupdate(self, timecost):         #buff不刷新的时候应用的函数
        self.dy.duration = max(self.dy.duration - timecost, 0)
        if self.dy.duration == 0 or self.dy.count == 0:
            self.end()

    def refresh(self, timecost, timenow, hitnumber):                # 新触发，通过外部的程序逻辑，判断buff要触发了，就要调用这个函数。
        self.readyjudge(timenow)                                    # 触发内置CD的判断
        if self.ft.alltime:                                         # 判断是否是常驻buff
            self.dy.duration = float('inf')                         # 赋值为无限大
            self.dy.count = self.ft.maxcount
            self.dy.active = True
            self.dy.last = timenow
        else:                                                       # 如果不是常驻buff再进入详细判断
            if not self.dy.ready:
                self.timeupdate(timecost)
            else:
                if not self.ft.fresh:                               # 如果是重复触发不刷新持续时间类型的buff，
                    self.timeupdate(timecost)
                else:
                    self.re_time(timecost)
                self.re_count(hitnumber, timecost)
                self.dy.last = timenow
                self.dy.ready = False
                   
    def active_judge(self, action, character):                      # 主判定函数
        if action in ['dash', 'breaked', 'switch', 'bwswitch']:
            action_judge = getattr(character.action, action)
        else:
            action_judge = getattr(character.action.attack, action)
        if self.ft.getlogic():
            for item in classkeydict:
                judge_condition = getattr(self.sjc, item)
                if judge_condition in [0, None]:
                    continue
                if judge_condition != action_judge[classkeydict[item]]:
                    return False
            return True
        else:
            try:
                exec(self.logic.xlogic)
            except Exception as e:
                print(f"Error executing logic: {e}")
    
    def buffchange(self, action, character, timecost, timenow, hitnumber):
        if self.active_judge(self, action, character):
            self.refresh(self, timecost, timenow, hitnumber)
        else:
            self.timeupdate(self, timecost)
        

