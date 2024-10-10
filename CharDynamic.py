from CharacterClass import Character
class CharacterDynamic:
    def __init__(self, startconfig, character:Character):
        self.normal = self.Normal_Statement(startconfig, character)
        self.special = self.Special_Resource()
    class Normal_Statement:
        def __init__(self, startconfig, character:Character):
            self.hp = character.outside.hp              # 生命值
            self.atk = character.outside.atk            # 攻击力
            self.defs = character.outside.defs          # 防御力
            self.bs = character.outside.bs              # 基础值
            self.cr = character.outside.cr              # 暴击率
            self.cd = character.outside.cd              # 暴击伤害
            self.eap = character.outside.eap            # 异常掌控
            self.em = character.outside.em              # 异常精通
            self.pr = character.outside.pr              # 穿透率
            self.pd = character.outside.pd              # 穿透值
            self.spr = character.outside.spr            # 能量自动回复
            self.spgr = character.outside.spgr          # 能量获得效率
            self.spm = character.outside.spm            # 能量上限
            self.phy = character.outside.phy            # 物理伤害加成
            self.fir = character.outside.fir            # 火属性伤害加成
            self.ice = character.outside.ice            # 冰属性伤害加成
            self.ele = character.outside.ele            # 电属性伤害加成
            self.eth = character.outside.eth            # 以太属性加成
            self.field = False                          # 是否位于前台
            self.sp = startconfig['StartSp']            # 起手能量
            self.fev = startconfig['StartFev']          # 起手喧响
    class Special_Resource:
        def __init__(self):
            self.resource: int = 0
            self.resour_name: str = None
            self.buff: bool = None
            self.buff_name: str = None
class Ellen(CharacterDynamic):
    def __init__(self, startconfig, character: Character):
        super().__init__(startconfig, character)
        self.special.resource = 0
        self.special.resour_name = '急冻'