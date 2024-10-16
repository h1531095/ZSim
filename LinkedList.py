class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None


class NodeIterator:
    def __init__(self, head):
        self.current = head

    def __next__(self):
        if self.current is None:
            raise StopIteration
        data = self.current.data
        self.current = self.current.next
        return data

    def __iter__(self):
        return self

'''    def __len__(self):
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count
    
    def __getitem__(self, index):
        current = self.head
        for _ in range(index):
            if current is None:
                raise IndexError("Index out of range")
            current = current.next
        return current.data
    
    def __setitem__(self, index, value):
        current = self.head
        for _ in range(index):
            if current is None:
                raise IndexError("Index out of range")
            current = current.next
        current.data = value'''


class LinkedList:
    def __init__(self):
        self.head = None

    def add(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def pop_head(self):
        if self.head is not None:
            removed_data = self.head.data
            self.head = self.head.next
            return removed_data
        else:
            return None

    def __iter__(self):
        return NodeIterator(self.head)

    def __str__(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return str(elements)

    def print_list(self):
        current = self.head
        while current:
            print(f"{current.data} -> ", end="")
            current = current.next
        print("None")


if __name__ == "__main__":
    # 使用示例
    sll = LinkedList()
    sll.add(1)
    sll.add(2)
    sll.add(3)

    # 打印链表
    sll.print_list()  # 输出: 1 -> 2 -> 3 -> None

    # 使用 for 循环遍历链表
    for data in sll:
        print(data)  # 输出: 1 2 3

    # 删除头部节点
    removed = sll.pop_head()
    print(f"Removed: {removed}")  # 输出: Removed: 1

    # 再次打印链表
    sll.print_list()  # 输出: 2 -> 3 -> None

    # 再次使用 for 循环遍历链表
    for data in sll:
        print(data)  # 输出: 2 3

    # 直接打印链表
    print(sll)  # 输出: [2, 3]
