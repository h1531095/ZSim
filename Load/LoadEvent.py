import Load
import Dot

global event_list, load_mission_dict


def LoadEvent():
    global event_list, load_mission_dict
    for key, mission in load_mission_dict.items():
        if isinstance(mission, Load.LoadingMission):
            pass
        elif isinstance(mission, Dot.Dot):
            pass

    pass
