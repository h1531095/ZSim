from .BuffAdd import buff_add
from .BuffExist_Judge import buff_exist_judge, change_name_box
from .BuffLoad import BuffLoadLoop, BuffInitialize
from .buff_class import Buff
from .ScheduleBuffSettle import ScheduleBuffSettle
from .JudgeTools import *
from .buff_class import spawn_buff_from_index


# TODO:
#  buff.ft.label = {"only_CoAttack": 1, "only_技能skill_tag": 1}
#   skill.label = {"CoAttack": 1, "accept_buff_Buff名字": 1}
#   按照如上格式，进行Buff的数据库拓展，并且写好构造函数的对应接口。