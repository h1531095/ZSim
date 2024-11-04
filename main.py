from dataclasses import dataclass

from Buff.BuffExist_Judge import buff_exist_judge
from SkillEventSplit import SkillEventSplit
from Buff.BuffLoad import BuffLoadLoop
from Update_Buff import update_dynamic_bufflist
import Skill_Class
import tqdm
import Preload
from Buff.BuffAdd import buff_add
from Report import write_to_csv

@dataclass
class Data:
    name_box = ['艾莲', '苍角', '莱卡恩']
    char_obj_list = []
    Judge_list_set = [['艾莲', '深海访客', '极地重金属'],
                      ['苍角', '含羞恶面', '自由蓝调'],
                      ['莱卡恩', '拘缚者', '镇星迪斯科']]
    weapon_dict = {'艾莲': ['深海访客', 1],
                   '苍角': ['含羞恶面', 5],
                   '莱卡恩': ['拘缚者', 1]}

def main_loop():
    pass