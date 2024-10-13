from CharSet_new import Character
from EnemyClass import Enemy
from define import *


# from BuffExsist_Judge import buff_exsist_judge

class Caculator:
    def __init__(self, char_statement: Character, enemy_statement: Enemy):
        self.char_statement = char_statement
        self.char_level = char_statement.level
        self.enemy_statement = enemy_statement

    def cal_dmg_expect(self, char_statement, enemy_statement):
        dmg_expect = 0
        return dmg_expect

    def cal_dmg_crit(self, char_statement, enemy_statement):
        dmg_crit = 0
        return dmg_crit

    def cal_dmg_not_crit(self, char_statement, enemy_statement):
        dmg_not_crit = 0
        return dmg_not_crit

    def cal_anomaly_dmg(self, char_statement, enemy_statement):
        anomaly_dmg_expect = 0
        return anomaly_dmg_expect

    def cal_anomaly_buildup(self, char_statement, enemy_statement):
        anomaly_buildup_expect = 0
        return anomaly_buildup_expect

    @staticmethod
    def cal_stun_buildup(self, char_statement, enemy_statement):
        stun_buildup_expect = 0
        return stun_buildup_expect


if __name__ == '__main__':
    char = Character(name='柳')
