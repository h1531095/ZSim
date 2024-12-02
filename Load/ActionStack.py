class ActionStack:
    """
    这个动作栈无法记录所有的动作，只能记录所有的前台角色的主动技能。
    功能类似于wow的插件TrufigGCD。但是长度只有2，因为只需要记录“上一个动作”和“当前动作”
    """
    def __init__(self):
        # 初始化一个空的栈
        self.stack = []

    def push(self, item):
        """向栈中压入一个元素，如果栈内元素超过2个，移除最早的元素"""
        self.stack.append(item)
        # 如果栈的大小超过 2，就删除栈底元素（即最先加入的元素）
        if len(self.stack) > 2:
            self.stack.pop(0)  # pop(0) 移除栈底元素

    def pop(self):
        """从栈顶弹出一个元素"""
        if self.is_empty():
            print("栈为空，无法弹出元素！")
            return None
        else:
            return self.stack.pop()

    def peek(self):
        """查看栈顶元素"""
        if not self.is_empty():
            return self.stack[-1]
        else:
            print("栈为空！")
            return None

    def is_empty(self):
        """判断栈是否为空"""
        return len(self.stack) == 0

    def size(self):
        """返回栈中元素的个数"""
        return len(self.stack)

