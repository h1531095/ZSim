from .character import Character
from .skill_class import Skill, lookup_name_or_cid

def character_factory(
                 name: str = '', CID: int = None,  # 角色名字和CID-必填至少一个
                 weapon=None, weapon_level=1,  # 武器名字-选填项
                 equip_set4=None, equip_set2_a=None, equip_set2_b=None, equip_set2_c=None,  # 驱动盘套装-选填项
                 drive4=None, drive5=None, drive6=None,  # 驱动盘主词条-选填项
                 scATK_percent=0, scATK=0, scHP_percent=0, scHP=0, scDEF_percent=0, scDEF=0, scAnomalyProficiency=0,
                 scPEN=0, scCRIT=0,  # 副词条数量-选填项
                 sp_limit=120,  # 能量上限-默认120
                 cinema=0
) -> Character:
    name, CID = lookup_name_or_cid(name, CID)
    char_init_args = {
        'name': name,
        'CID': CID,
        'weapon': weapon,
        'weapon_level': weapon_level,
        'equip_set4': equip_set4,
        'equip_set2_a': equip_set2_a,
        'equip_set2_b': equip_set2_b,
        'equip_set2_c': equip_set2_c,
        'drive4': drive4,
        'drive5': drive5,
        'drive6': drive6,
        'scATK_percent': scATK_percent,
        'scATK': scATK,
        'scHP_percent': scHP_percent,
        'scHP': scHP,
        'scDEF_percent': scDEF_percent,
        'scDEF': scDEF,
        'scAnomalyProficiency': scAnomalyProficiency,
        'scPEN': scPEN,
        'scCRIT': scCRIT,
        'sp_limit': sp_limit,
        'cinema': cinema
    }
    if name == '苍角':
        from .Soukaku import Soukaku
        return Soukaku(**char_init_args)
    elif name == '莱特':
        from .Lighter import Lighter
        return Lighter(**char_init_args)
    elif name == '艾莲':
        from .Ellen import Ellen
        return Ellen(**char_init_args)
    elif name == '雅':
        from .Miyabi import Miyabi
        return Miyabi(**char_init_args)
    elif name == '11号':
        from .Soldier11 import Soldier11
        return Soldier11(**char_init_args)
    else:
        return Character(**char_init_args)
