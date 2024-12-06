import random

class Node:
    def __init__(self, parent, left_child, right_child) -> None:
        self.parent = parent
        self.left_child = left_child
        self.right_child = right_child

class CueNode(Node):
    def __init__(self, parent, is_inverted, situation_index, left_child, right_child) -> None:
        super().__init__(parent, left_child, right_child)
        self.situation_index = situation_index
        self.is_inverted = is_inverted

    @classmethod
    def cue_node_factory(cls, parent, situation_num):
        return CueNode(
                parent= parent, 
                is_inverted= random.choice([True, False]), 
                situation_index= random.randint(0, situation_num-1), 
                left_child= None, 
                right_child= None
            )

    def decide(self, situation):
        if situation[self.situation_index] != self.is_inverted:
            return self.left_child
        return self.right_child

class ActionNode(Node):
    def __init__(self, parent, action, left_child, right_child) -> None:
        super().__init__(parent, left_child, right_child)
        self.action = action

class Tree:
    def __init__(self, depth, actions, situation_amount) -> None:
        self.root = CueNode.cue_node_factory(None, situation_amount)
        self.root.left_child = CueNode.cue_node_factory(self.root, situation_amount)
        self.actions = actions
        self.situation_amount = situation_amount
        self.build_tree(self.root.left_child, depth)

    def build_tree(self, node, depth):
        if depth <= 0:
            node.left_child = ActionNode(
                parent= node, 
                action= random.choice(self.actions),
                left_child= None,
                right_child= None
            )
            return

        node.right_child = ActionNode(
                parent= node, 
                action= random.choice(self.actions),
                left_child= None,
                right_child= None
            )
        
        if random.uniform(0, 1) <= 0.5:
            node.left_child = CueNode.cue_node_factory(node, self.situation_amount)
            self.build_tree(node.left_child, depth - 1)
        else:
            node.left_child = ActionNode(
                parent= node, 
                action= random.choice(self.actions),
                left_child= None,
                right_child= None
            )

    def get_action(self, situation):    
        def get_action_rec(situation, node):
            if isinstance(node, ActionNode):
                return node.action
            newNode = node.decide(situation)
            if newNode is None:
                if isinstance(node.left_child, ActionNode):
                    return node.left_child.action
                return node.left_child.decide(situation)
            return get_action_rec(situation, newNode)
        return get_action_rec(situation, self.root)
    
     
    def random_traverse(self):
        current = self.root.left_child
        take_next_step = random.uniform(0, 1)
        while take_next_step <= 0.6:
            if isinstance(current.left_child, ActionNode):
                break
            current = current.left_child
            take_next_step = random.uniform(0, 1)
        return current

class ToolBox:
    def __init__(self, depth, actions, situation_amount):
        self.trees = []
        for _ in range(3):
            self.trees.append(Tree(depth= depth, actions= actions, situation_amount= situation_amount))

    def get_action(self, situation):
        for tree in self.trees:
            if tree.root.decide(situation) is not None:
                return tree.get_action(situation)
        return self.trees[0].get_action(situation)

    def random_traverse(self, key):
        return self.selector[key].random_traverse()


