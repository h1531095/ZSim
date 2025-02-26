import unittest
from sim_progress.Character import Character


class TestCharacter(unittest.TestCase):
    def test_init_character(self):
        char = Character(name="柳", weapon='时流贤者',
                         equip_set4='混沌爵士', equip_set2_a='雷暴重金属',
                         drive4='异常精通', drive5='电属性伤害%', drive6='异常掌控',
                         scAnomalyProficiency=10, scATK_percent=14, scCRIT=4)
        self.assertEqual(char.NAME, "柳")
        char_static = char.statement
        skill_object = char.skill_object
        skill_object.get_skill_info(skill_tag=char.action_list[0], attr_info='damage_ratio')