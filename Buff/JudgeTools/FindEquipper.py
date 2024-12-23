from .FindMain import find_main


def find_equipper(item_name: str):
    """
    该函数用来找佩戴装备的人，但是需要注意，这个函数处理不了多个人同时佩戴同一件装备的情况。
    """
    main_module = find_main()
    Judge_list_set = main_module.init_data.Judge_list_set
    for sub_list in Judge_list_set:
        for i in sub_list:
            if i == item_name:
                return sub_list[0]