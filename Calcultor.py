from CharSet_new import Character
from EnemyClass import Enemy
from define import *


# from BuffExist_Judge import buff_exist_judge

class Caculator:
    def __init__(self, char_statement: Character, enemy_statement: Enemy):
        self.char_statement = char_statement
        self.char_level = char_statement.level
        self.enemy_statement = enemy_statement

    @staticmethod
    def cal_dmg_expect(char_statement, enemy_statement):
        dmg_expect = 0
        return dmg_expect

    @staticmethod
    def cal_dmg_crit(char_statement, enemy_statement):
        dmg_crit = 0
        return dmg_crit

    @staticmethod
    def cal_dmg_not_crit(char_statement, enemy_statement):
        dmg_not_crit = 0
        return dmg_not_crit

    @staticmethod
    def cal_anomaly_dmg(char_statement, enemy_statement):
        anomaly_dmg = 0
        return anomaly_dmg

    @staticmethod
    def cal_anomaly_dmg_equally():
        anomaly_dmg_equally = 0
        return anomaly_dmg_equally

    @staticmethod
    def cal_anomaly_buildup(char_statement, enemy_statement):
        anomaly_buildup_expect = 0
        return anomaly_buildup_expect

    @staticmethod
    def cal_stun_buildup(self, char_statement, enemy_statement):
        stun_buildup_expect = 0
        return stun_buildup_expect


if __name__ == '__main__':
    char = Character(name='柳')