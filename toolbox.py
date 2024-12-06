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
    
    def __str__(self): 
        return ("!" if self.is_inverted else "")+"c"+str(self.situation_index) 
    
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
    def __str__(self): 
        return "a"+str(self.action)
 
class Tree:
    def __init__(self, depth, actions, situation_amount) -> None:
        self.root = CueNode.cue_node_factory(None, situation_amount)
        self.root.left_child = CueNode.cue_node_factory(self.root, situation_amount)
        self.actions = actions
        self.situation_amount = situation_amount
        self.build_tree(self.root.left_child, depth)

    def show(self):
        current = self.root
        prev = None
        while not isinstance(current, ActionNode):
            if current == prev:
                print(str(prev), str(prev.right_child), str(prev.left_child))
                raise ValueError("loooop in tree")
            print(f"{current}-{current.right_child}")
            print("|")
            prev = current
            current = current.left_child
        print(f"{current}")
        print()

    def add_cue_action_pair(self, at_node):
        newCueNode = CueNode.cue_node_factory(at_node, self.situation_amount)
        newCueNode.right_child = ActionNode(
            parent= newCueNode, 
            action= random.choice(self.actions),
            left_child= None,
            right_child= None
        )
        newCueNode.parent = at_node
        newCueNode.left_child = at_node.left_child  # The new node points to the next node
        at_node.left_child = newCueNode  # The previous node points to the new node
        if newCueNode.left_child is not None:
            newCueNode.left_child.parent = newCueNode

        return newCueNode.left_child

    def delete_node(self, node):
        # delete the current node
        nextNode = node.left_child
        node.parent.left_child = node.left_child
        node.left_child.parent = node.parent
        return nextNode

    def swap_nodes(self, n1, n2):
        n1.situation_index, n2.situation_index = n2.situation_index, n1.situation_index
        n1.is_inverted, n2.is_inverted = n2.is_inverted, n1.is_inverted

        n1.right_child.action, n2.right_child.action = n2.right_child.action, n1.right_child.action

    def build_tree(self, node, depth):
        if depth <= 0:
            node.left_child = ActionNode(
                parent= node, 
                action= random.choice(self.actions),
                left_child= None,
                right_child= None
            )
            node.right_child = ActionNode(
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
            if isinstance(current.left_child, ActionNode) or isinstance(current, ActionNode):
                break
            current = current.left_child
            take_next_step = random.uniform(0, 1)
        return current

class ToolBox:
    def __init__(self, depth, actions, situation_amount):
        self.trees = []
        for _ in range(3):
            self.trees.append(Tree(depth= depth, actions= actions, situation_amount= situation_amount))

    def show(self):
        for tree in self.trees:
            tree.show()

    def get_action(self, situation):
        for tree in self.trees:
            if tree.root.decide(situation) is not None:
                return tree.get_action(situation)
        return self.trees[0].get_action(situation)

    def random_traverse(self, key):
        return self.selector[key].random_traverse()

if __name__ == '__main__':
    tb = ToolBox(10, [1,2,3], 5)
    tb.trees[0].show()
    tb.trees[0].add_cue_action_pair(tb.trees[0].root.left_child)
    tb.trees[0].show()
    tb.trees[0].delete_node(tb.trees[0].root.left_child)
    tb.trees[0].show()
    tb.trees[0].swap_nodes(tb.trees[0].root.left_child, tb.trees[0].root.left_child.left_child)
    tb.trees[0].show()