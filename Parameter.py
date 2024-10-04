def get_parameter(prompt, validation_func=None):        #判断函数，prompt是输入参数，而后面的则是条件表达式
    while True:
        value = input(prompt)
        try:
            if validation_func and not validation_func(value):
                print("输入不符合要求，请重新输入。")
                continue
            return value
        except ValueError:
            print("请输入有效的参数。")