import sys


def find_main():
    main_module = sys.modules["__main__"]
    return main_module


def find_enemy():
    main_module = find_main()
    enemy = main_module.schedule_data.enemy
    return enemy


def find_init_data():
    main_module = find_main()
    init_data = main_module.init_data
    return init_data


def find_char_list():
    main_module = find_main()
    char_list = main_module.char_data.char_obj_list
    return char_list


def find_dynamic_buff_list():
    main_module = find_main()
    dynamic_buff_list = main_module.global_stats.DYNAMIC_BUFF_DICT
    return dynamic_buff_list
