def detect_edge(pair, mode_func):
    # 使用自定义的mode_func函数来判断是否为上升沿或下降沿
    return mode_func(pair[0], pair[1])


if __name__ == "__main__":
    list1 = [False, True]
    mode_func = lambda a, b: a is False and b is True
    a = detect_edge(list1, mode_func)
    print(a)
