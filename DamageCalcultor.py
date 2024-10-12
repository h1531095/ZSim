from CharSet_new import Character
from EnemyClass import Enemy
# from BuffExsist_Judge import buff_exsist_judge

class Caculator:
    def __init__(self, char_statement:Character, enemy_statement:Enemy):
        self.char_statement = char_statement
        self.char_level = char_statement.level
        self.enemy_statement = enemy_statement
        self.dmg_expect, self.dmg_crit, self.dmg_not_crit = self.cal_dmg(char_statement, enemy_statement)
    
    def cal_dmg(self, char_statement, enemy_statement):
        dmg_expect = 0
        dmg_crit = 0
        dmg_not_crit = 0
        return dmg_expect, dmg_crit, dmg_not_crit