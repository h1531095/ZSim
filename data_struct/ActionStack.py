class ActionStack:
    """
    这个动作栈无法记录所有的动作，只能记录所有的前台角色的主动技能。
    功能类似于wow的插件TrufigGCD。但是长度只有2，因为只需要记录“上一个动作”和“当前动作”
    """
    def __init__(self):
        # 初始化一个空的栈，用列表作为基础
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
            return None
        else:
            return self.stack.pop()

    def peek(self):
        """查看栈顶元素"""
        if not self.is_empty():
            return self.stack[-1]
        else:
            return None

    def is_empty(self):
        """判断栈是否为空"""
        return len(self.stack) == 0

    def peek_bottom(self):
        """查看栈底元素"""
        if not self.is_empty():
            return self.stack[0]
        else:
            return None

    def __len__(self): 
        return len(self.stack)
    
    def __str__(self):
        return str(self.stack)
    
    def __iter__(self): 
        return iter(self.stack)
    
    def __getitem__(self, index):
        return self.stack[index]
    
    def __eq__(self, value: object) -> bool:
        return self.stack == value or self.stack == getattr(value, 'stack', None)
    
    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)
    