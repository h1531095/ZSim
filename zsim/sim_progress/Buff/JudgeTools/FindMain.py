import sys


def find_main():
    main_module = sys.modules["simulator.main_loop"]
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


def find_tick():
    main_module = find_main()
    tick = main_module.tick
    return tick


def find_exist_buff_dict():
    main_module = find_main()
    exist_buff_dict = main_module.load_data.exist_buff_dict
    return exist_buff_dict


def find_event_list():
    main_module = find_main()
    event_list = main_module.schedule_data.event_list
    return event_list


def find_stack():
    main_module = find_main()
    stack = main_module.load_data.action_stack
    return stack


def find_load_data():
    main_module = find_main()
    load_data = main_module.load_data
    return load_data


def find_preload_data():
    main_module = find_main()
    preload_data = main_module.preload.preload_data
    return preload_data


def find_name_box():
    main_module = find_main()
    name_box = main_module.load_data.name_box
    return name_box


def find_all_name_order_box():
    main_module = find_main()
    all_name_order_box = main_module.load_data.all_name_order_box
    return all_name_order_box
