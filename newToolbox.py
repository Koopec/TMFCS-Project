from bigtree import BinaryNode, print_tree
import random

class CueNode(BinaryNode):
    def __init__(self, is_inverted, situation_index, left=None, right=None, parent=None):
        super().__init__(left= left, right= right, parent= parent)
        self.is_inverted = is_inverted
        self.situation_index = situation_index
        self.name = ("!" if self.is_inverted else "")+"c"+str(self.situation_index)

    def decide(self, situation):
        if situation[self.situation_index] != self.is_inverted:
            return self.left
        return self.right

class ActionNode(BinaryNode):
    def __init__(self, action, left=None, right=None, parent= None):
        super().__init__(parent=parent, left=left, right=right)
        self.action = action
        self.name = "a"+str(self.action)

class Tree():
    def __init__(self, depth, actions, situation_amount) -> None:
        self.root = CueNode(
            random.choice([True, False]), 
            random.randint(0, situation_amount-1))
        tmp = CueNode(
            random.choice([True, False]), 
            random.randint(0, situation_amount-1),
            parent= self.root)
        self.actions = actions
        self.situation_amount = situation_amount
        self.build_tree(tmp, depth)
    
    def copy(self):
        nt = Tree(3,range(0,2),3)
        nt.root = self.root.copy()
        nt.situation_amount = self.situation_amount
        nt.actions = self.actions 
        return nt

    def build_tree(self, node, depth):
        if depth <= 0:
            ActionNode(parent= node, action= random.choice(self.actions))
            ActionNode(parent= node, action= random.choice(self.actions))
            return
        
        if random.uniform(0, 1) <= 0.5:
            CueNode(    
                random.choice([True, False]), 
                random.randint(0, self.situation_amount-1),
                parent= node)
            self.build_tree(node.left, depth - 1)
        else:
            ActionNode(parent= node, action= random.choice(self.actions))

        ActionNode(parent= node, action= random.choice(self.actions))

    def get_action(self, situation):    
        def get_action_rec(situation, node):
            if isinstance(node, ActionNode):
                return node.action
            newNode = node.decide(situation)
            if newNode is None:
                if isinstance(node.left, ActionNode):
                    return node.left.action
                return get_action_rec(situation, node.left)
            return get_action_rec(situation, newNode)
        return get_action_rec(situation, self.root)
    
    def random_traverse(self):
        current = self.root.left
        take_next_step = random.uniform(0, 1)
        while take_next_step <= 0.6:
            if isinstance(current.left, ActionNode) or isinstance(current, ActionNode):
                break
            current = current.left
            take_next_step = random.uniform(0, 1)
        return current


    def swap_nodes(self, n1, n2):
        if n1 == n2:
            return
        if n1.depth < n2.depth:
            n1, n2 = n2, n1

        l1, r1 = n1.left, n1.right
        l2, r2 = n2.left, n2.right
        p1 = n1.parent
        p2 = n2.parent

        n1.left = None
        n1.right = None
        n2.left = None
        n2.right = None
        n1.parent = None
        n2.parent = None

        if p1 == n2:
            n2.parent = n1
        else:
            n2.parent = p1
        if p2 == n1:
            n1.parent = n2
        else:
            n1.parent = p2

        n2.right = r1
        n1.right = r2

        if l1 == n2:
            n2.left = n1
        else:
            n2.left = l1
        
        if l2 == n1:
            n1.left = n2
        else:
            n1.left = l2
     
    def delete_node(self, node):
        p = node.parent
        l = node.left
        p.left = None
        l.parent = None
        p.left = l
        l.parent = p
        return l

    def add_cue_action_pair(self, n1):
        new_cue_node = CueNode(
            random.choice([True, False]), 
            random.randint(0, self.situation_amount-1))
        n2 = n1.left
        n1.left = None
        new_cue_node.parent = n1
        new_cue_node.left = n2
        n2.parent = new_cue_node
        n1.left = new_cue_node

        ActionNode(
            parent= new_cue_node, 
            action= random.choice(self.actions))
        return new_cue_node.left

class ToolBox:
    def __init__(self, depth, actions, situation_amount):
        self.trees = []
        for _ in range(5):
            self.trees.append(Tree(depth= depth, actions= actions, situation_amount= situation_amount))
    
    def copy(self):
        newTrees = []
        for tree in self.trees:
            newTrees.append(tree.copy())
        nt = ToolBox(3,range(0,2),3)
        nt.trees = newTrees
        return nt

    def show(self):
        for tree in self.trees:
            tree.show()

    def get_action(self, situation):
        for tree in self.trees:
            if tree.root.decide(situation) is not None:
                return tree.get_action(situation)
        return self.trees[0].get_action(situation)

if __name__ == "__main__":
    print("lol")
    t1 = Tree(depth= 3, actions=range(0,10), situation_amount= 10)
    t1.root.show()
    t1.swap_nodes(t1.root.left.left, t1.root.left)
    t1.root.show()
    t1.delete_node(t1.root.left.left)
    t1.root.show()
    t1.add_cue_action_pair(t1.root.left)
    t1.root.show()

