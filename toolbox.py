import random

class Node:
    def __init__(self, parent, left_child, right_child) -> None:
        self.parent = parent
        self.left_child = left_child
        self.right_child = right_child

class CueNode(Node):
    def __init__(self, parent, is_inverted, situation_index, left_child, right_child) -> None:
        super.__init__(parent, left_child, right_child)
        self.situation_index = situation_index
        self.is_inverted = is_inverted

    @classmethod
    def cue_node_factory(cls, parent, situation_num):
        return CueNode(
                parent= parent, 
                is_inverted= random.choice([True, False]), 
                situation_index= random.randint(0, situation_num), 
                left_child= None, 
                right_child= None
            )

    def decide(self, situation):
        if situation[self.situation_index] != self.is_inverted:
            return self.left_child
        return self.right_child

class ActionNode(Node):
    def __init__(self, parent, action, left_child, right_child) -> None:
        super.__init__(parent, left_child, right_child)
        self.action = action

class Tree:
    def __init__(self, depth, actions, situation_amount) -> None:
        self.root = CueNode.cue_node_factory(None, situation_amount)
        self.root.left_child = CueNode.cue_node_factory(self.root, situation_amount)
        self.actions = actions
        self.situation_amount = situation_amount
        self.build_tree(self.root.left_child, depth)

    def build_tree(self, node, depth):
        if depth < 0:
            return

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

        if random.uniform(0, 1) <= 0.5:
            node.right_child = CueNode.cue_node_factory(node, self.situation_amount)
            self.build_tree(node.right_child, depth - 1)
        else:
            node.right_child = ActionNode(
                parent= node, 
                action= random.choice(self.actions),
                left_child= None,
                right_child= None
            )

    def get_action(self, situation):    
        def get_action_rec(situation, node):
            if node is ActionNode:
                return node.action
            newNode = node.decide(situation)
            return get_action_rec(situation, newNode)
        return get_action_rec(situation, self.root)
    
     
    def random_traverse(self):
        current = self.root
        take_next_step = random.uniform(0, 1)
        while take_next_step <= 0.6:
            go_left = random.uniform(0, 1)
            if go_left <= 0.5:
                current = current.left_child
            else:
                current = current.right_child
            take_next_step = random.uniform(0, 1)
            if current is ActionNode:
                break
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

p = 0.5 

DEPTH = 10
ACTIONS = range(1,50)
SITUATION_AMOUNT = 10

world = ToolBox(depth= DEPTH, actions= ACTIONS, situation_amount= SITUATION_AMOUNT)    
population = [ToolBox(depth= 10, actions= range(1, 50)) for _ in range(500)]

while 0 < len(population) < 600:
    situations = [[random.choice([True,False]) for _ in range(10)] for _ in range(1000)]
    for individual in population: # remove underperforming individuals
        fitness = fitness(individual, world, situations) 
        d = (1 - p)**fitness
        k = random.uniform(0, 1)
        if k > d:
            population = population.remove(individual)
    newPopulation = []
    for individual in population: # choose two parents, choose num of children, crossover & mutate heuristics for children
        parent1 = individual
        num_children = 1
        k = random.uniform(0, 1)
        if k <= 0.474:
            num_children = 2
        for i in range(num_children):
            parent2 = random.sample(population, 1)
            k = random.uniform(0,1) # not needed? 
            child = crossover(parent1, parent2)
            child = mutate(child)
            newPopulation.append(child)
    population = newPopulation
    
def crossover(parent1, parent2):
    p1 = random.uniform(0, 1)
    if p1 <= 0.1:
        p2 = random.uniform(0, 1)
        if p2 <= 0.5:
            c1 = random.randint(len(parent1.trees))
            c2 = random.randint(len(parent2.trees))
            parent1[c1] = parent2[c2]
            return parent1
        else:
            for h1, h2 in zip(parent1.trees, parent2.trees):
                node1 = h1.random_traverse()
                node2 = h2.random_traverse()
                node1.left_child = node2
            return parent1
    else:
        return parent1

def mutate(child):
    copyList = child.trees.copy()
    for i in range(len(child.trees)):
        p1 = random.uniform(0,1)
        if p1 <= 0.11:
            p2 = random.uniform(0,1)
            if p2 < 0.25:
                # Change selector cue

                pass
            elif p2 < 0.50:
                child.trees = copyList.insert(i+1,)
            elif p2 < 0.75:
                # Delete selector cue
                del copyList[i]
            else:
                # swap two selector cues
                pass
    

def fitness(toolbox,world,situations):
    score = 0
    for situation in situations:
        if toolbox.get_action(situation) == world.get_action(situation):
            score +=1
    return len(situations) - score

