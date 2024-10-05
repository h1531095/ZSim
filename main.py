from CharSet import character_set       #录入角色配置信息的函数
from CharacterClass import Character    #Character类
from EnemyClass import Enemy
from EnemySet import enemyset
from KCalculate import Kcal
charnum, charname_box, charactive_box = character_set()   #charnum是实际角色数量。charname_box 是三个角色名；而charactive_box是三个实例化的角色；
enemyactive = enemyset()
print(charactive_box[0].bonus.cr)
