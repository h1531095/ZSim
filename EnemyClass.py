class Enemy:
    def __init__(self, config):
        self.info = self.EnemyInformation(config)
        self.stat = self.Enemystatement(config)
        self.re = self.EnemyResist(config)
    class EnemyInformation:
        def __init__(self, config):
            self.id = float(config['ID'])
            self.name = config['Name']
            self.type = config['Type']
            self.level = float(config['Level'])
    class Enemystatement:
        def __init__(self, config):
            self.hp = float(config['Hp'])
            self.atk = float(config['Atk'])
            self.defe = float(config['Def'])
            self.stun = float(config['Stun'])
            self.stdtr = float(config['StunDamageTakeRatio'])
            self.strc = float(config['StunResetCount'])
            self.elea = float(config['ElementAbnormal'])
    class EnemyResist:
        def __init__(self, config):
            self.pr = float(config['PhyResist'])
            self.fr = float(config['FireResist'])
            self.ir = float(config['IceResist'])
            self.elr = float(config['EleResist'])
            self.etr = float(config['EthResist'])