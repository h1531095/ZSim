from EnemyClass import Enemy
from CharacterClass import Character
from KCalculate import Kcal
from BonusCalculate import BonusCal
class Multi:
    def __init__(self, character, enemy, muldict):
        self.dmg = self.Damage_Bonus(muldict)
        self.defence = self.Defense_Zone(character, muldict)
        self.res = self.Resistance_Zone(enemy, muldict)
        self.crit = self.Crit_Zone(character, muldict)
        self.vul = self.Vulnerability_Zone(muldict)
        self.stdmg = self.StunDamage_TakeRatio(enemy, muldict)
        self.special = self.Special_Multiplication_Zone(muldict)
    class Damage_Bonus:
        def __init__(self,muldict):
            self.element = self.Element_Bonus(muldict)
            self.atktype = self.Attack_Type(muldict)
            self.skitype = self.Skill_Type(muldict)
            self.all = self.All_Dmg(muldict)
        class Element_Bonus:
            def __init__(self, muldict):
                self.phy = muldict['PhyBonus']
                self.fire = muldict['FireBonus']
                self.ice = muldict['IceBonus'] 
                self.ele = muldict['EleBonus']
                self.eth = muldict['EthBonus']
        class Attack_Type:
            def __init__(self, muldict):
                self.atktype = float(muldict['AttackType'])
        class Skill_Type:
            def __init__(self, muldict):
                self.na = float(muldict['NormalAttack'])                #普攻
                self.e = float(muldict['SpecialSkill'])                 #特殊技
                self.ex = float(muldict['ExSpecial'])                   #强化特殊技
                self.da = float(muldict['Dashattack'])                  #冲刺攻击
                self.aa= float(muldict['Avoidattack'])                  #闪避反击
                self.qte = float(muldict['QTE'])                        #连携技
                self.q = float(muldict['Q'])                            #大招
                self.bh = float(muldict['BHaid'])                       #受击支援
                self.pa = float(muldict['Parryaid'])                    #回避支援
                self.ass = float(muldict['Assaultaid'])                 #支援突击
                self.ele = float(muldict['ElementalStatus'])            #元素异常倍率
        class All_Dmg:
            def __init__(self, muldict):
                self.value = float(muldict['ALLDMG'])
    class Defense_Zone:
        #防御区有众多参数，有直接和怪物属性挂钩的，也有和其他内容挂钩的
        #这里涉及的内容有：
            #固定值：敌方基础防御，敌方等级，攻击方等级（以及依靠改数据计算出的攻击方等级基数）
            #动态属性： 攻击方穿透率，攻击方穿透值，敌方减防，固定防御
        def __init__(self, character, muldict):
            self.inc = muldict['Defincrease']
            self.dec = muldict['Defdecrease']
            self.fix = muldict['Deffix']
            self.pd = muldict['Pendelta']
            self.pdr = muldict['Pendelta_Ratio']
            self.k = Kcal(character)
    class Resistance_Zone:
        def __init__(self, enemy, muldict):
            #抗性区涉及的三个参数，其中，“受击方抗性”是一个固定值，和怪物种类有关，与伤害类型标签相似，这个参数共有五个类型，
            #分别是：PhyRes, FireRes, IceRes, EleRes, EthRes, ALL
            #此处应该是一个字典。
            #当然，这一个系列里面应该都是字典，因为是和抗性相关的，字典的键值是一样的，
            self.ele_res = self.Element_Res(enemy, muldict)
            self.ele_reduce = muldict['Element_reduce']             #受击方全抗性降低
            self.ele_penetrate = muldict['Element_penetrate']       #攻击方全抗性穿透
        class Element_Res:  #受击方抗性
            def __init__(self, enemy, muldict):
                self.phy = enemy.re.pr + muldict['PhyRes']
                self.fire = enemy.re.fr + muldict['FireRes']
                self.ice = enemy.re.ir + muldict['IceRes']
                self.ele = enemy.re.elr + muldict['EleRes']
                self.eth = enemy.re.etr + muldict['EthRes']
                self.all = muldict['AllRes']
    class Crit_Zone:
            #这个区的数据，只有双爆需要参与，而且一般计算的时候，是由随机数系统来控制暴击的，和这个区无关。
            #只有在计算期望的时候，才需要用到这个区的属性。
            #期望的计算 = 1 + 暴击率 * 暴击伤害
            def __init__(self, character, muldict):
                CRbasic = character.basic.cr                    #暴击率基础值
                CRBounus = character.bonus.cr                   #暴击率加成，列表
                CDBasic = character.basic.cd                    #爆伤基础值
                CDBonus = character.bonus.cd                    #爆伤加成，列表
                crictR = BonusCal(CRbasic, CRBounus)            #暴击率加成实例化，传到crictR里面
                crictD = BonusCal(CDBasic, CDBonus)             #爆伤加成实例化，传到crictD里面
                self.cbc = muldict['Chance_to_be_crit']         #被暴击的几率
                self.dfc = muldict['Damage_from_crit']          #受到的爆击伤害。
                self.cr = crictR + self.cbc                  #计算最终的暴击率值
                self.cd = crictD + self.dfc                  #计算最终的暴击伤害值                                
                #最终的双爆期望，这才是我们需要的数据
                self.CriticalExpect = 1 + (self.cr + self.cbc) * (self.cd + self.dfc)
    class Vulnerability_Zone:
        def __init__(self, muldict):
            self.di = muldict['Dmgtaken_Increase']      #受到伤害增加
            self.dd = muldict['Dmgtaken_Decrease']      #受到伤害减少
    #失衡易伤区
    class StunDamage_TakeRatio:
        def __init__(self, enemy, muldict):
            #失衡易伤倍率
            self.st = muldict['StunDamage_TakeRatio'] + enemy.stat.stdtr
            #易伤倍率增加
            self.std = muldict['StunDamage_TakeRatio_Delta']
    #特殊乘区
    class Special_Multiplication_Zone:
        def __init__(self, muldict):
            self.value = muldict['Special_Multiplication_Zone']    


