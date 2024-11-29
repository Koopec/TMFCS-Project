import random

class Node:
    def __init__(self, parent, action, left_child, right_child) -> None:
        self.parent = parent
        self.action = action
        self.left_child = left_child
        self.right_child = right_child

    def decide(self, value):
        if value:
            return self.left_child
        return self.right_child

class ToolBox:
    def __init__(self, depth, actions) -> None:
        self.root = Node(None, 0, None, None)
        self.actions = actions
        self.build_tree(self.root, depth)
    
    def build_tree(self, node, depth):
        if depth < 0:
            return

        node.left_child = Node(node, 0, None, None)
        node.right_child = Node(node, 0, None, None)
        if random.randint(0, 10) <= 5:
            self.build_tree(node.left_child, depth - 1)
        else:
            node.left_child.action = random.choice(self.actions)

        if random.randint(0, 10) <= 5:
            self.build_tree(node.right_child, depth - 1)
        else:
            node.right_child.action = random.choice(self.actions)

    def get_action(self, situation):
        current = self.root
        for value in situation:    
            current = current.decide(value)
            if current.action != 0:
                return current.action
        return current.action
            

tree = ToolBox(5, range(1,10))
print(tree.get_action([True, True, False, False, True]))

        
