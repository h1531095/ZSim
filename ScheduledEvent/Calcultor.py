from CharSet_new import Character
from Preload import SkillNode
from Enemy import Enemy
import copy
from BuffClass import Buff
from Report import report_to_log


# from BuffExist_Judge import buff_exist_judge

class MultiplierData:
    def __int__(self, skill: SkillNode, character: Character, enemy: Enemy, dynamic_buff: dict = None):
        if dynamic_buff is None:
            dynamic_buff = {}
        else:
            pass

        if not isinstance(skill, SkillNode):
            raise ValueError("错误的参数类型，应该为SkillNode")
        if not isinstance(character, Character):
            raise ValueError("错误的参数类型，应该为Character")
        if not isinstance(enemy, Enemy):
            raise ValueError("错误的参数类型，应该为Enemy")
        if not isinstance(dynamic_buff, dict):
            raise ValueError("错误的参数类型，应该为dict")

        self.char_name: str = character.NAME
        self.char_cid: int = character.CID

        try:
            self.char_buff: list = dynamic_buff[self.char_name]
        except KeyError:
            self.char_buff = []
            report_to_log(f"动态Buff列表内没有角色{self.char_name}", level=4)

        self.static_statement = copy.deepcopy(character.Statement)


if __name__ == '__main__':
    char = Character(name='柳')