from Skill_Class import Skill


class InitSkillSequence(Skill):
    def __init__(self, CID: int = None):
        super(InitSkillSequence, self).__init__(CID=CID)


skills = Skill(CID=1221)
initial_skill_sequence = InitSkillSequence(CID=1221)
pass