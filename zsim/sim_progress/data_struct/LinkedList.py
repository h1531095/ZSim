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
        data = self.current.preload_data
        self.current = self.current.next
        return data

    def __iter__(self):
        return self

class LinkedList:
    def __init__(self):
        self.head = None

    def add(self, data):
        """在链表尾部添加"""
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def insert(self, data):
        """在链表头部插入"""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def __iter__(self):
        return NodeIterator(self.head)

    def __str__(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.preload_data)
            current = current.next
        return str(elements)

    def __len__(self):
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count

    def __getitem__(self, index):
        current = self.head
        if current is None:
            raise IndexError("Index out of range")
        for _ in range(index):
            current = current.next
            if current is None:
                raise IndexError("Index out of range")
        return current.preload_data

    def print_list(self):
        current = self.head
        while current:
            print(f"{current.preload_data} -> ", end="")
            current = current.next
        print("None")

    def pop_head(self):
        if self.head is not None:
            removed_data = self.head.preload_data
            self.head = self.head.next
            return removed_data
        else:
            return None

    def remove(self, data):
        current = self.head
        previous = None
        while current:
            if current == data:
                if previous:
                    previous.next = current.next
                else:
                    self.head = current.next
                return True
            previous = current
            current = current.next
        return False
