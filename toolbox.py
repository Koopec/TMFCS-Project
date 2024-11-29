import random

class Node:
    def __init__(self, parent, action, situation_index, left_child, right_child) -> None:
        self.parent = parent
        self.action = action
        self.situation_index = situation_index
        self.left_child = left_child
        self.right_child = right_child

    def decide(self, situation):
        if situation[self.situation_index]:
            return self.left_child
        return self.right_child

class ToolBox:
    def __init__(self, depth, actions) -> None:
        self.root = Node(None, 0, depth, None, None)
        self.actions = actions
        self.situation_num = depth
        self.build_tree(self.root, depth)
    
    def build_tree(self, node, depth):
        if depth < 0:
            return

        node.left_child = Node(node, 0, random.randint(0, self.situation_num), None, None)
        node.right_child = Node(node, 0, random.randint(0, self.situation_num), None, None)
        if random.uniform(0, 1) <= 0.5:
            self.build_tree(node.left_child, depth - 1)
        else:
            node.left_child.action = random.choice(self.actions)

        if random.uniform(0, 1) <= 0.5:
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
            
    def random_traverse(self):
        current = self.root
        take_next_step = random.uniform(0, 1)
        while take_next_step <= 0.6:
            go_left = random.uniform(0, 1)
            if go_left:
                current = current.left_child
            else:
                current = current.right_child
            take_next_step = random.uniform(0, 1)
        return current

p = 0.5 

tree = ToolBox(5, range(1,10))
print(tree.get_action([True, True, False, False, True]))

world = ToolBox(depth= 10, actions= range(1, 50))    
population = [ToolBox(depth= 10, actions= range(1, 50)) for _ in range(500)]

while 0 < len(population) < 600:
    situations = [[random.choice([True,False]) for _ in range(10)] for _ in range(1000)]
    for individual in population:
        fitness = fitness(individual, world, situations) 
        d = (1 - p)**fitness
        k = random.uniform(0, 1)
        if k > d:
            population = population.remove(individual)
    newPopulation = []
    for individual in population:
        parent1 = individual
        num_children = 1
        k = random.uniform(0, 1)
        if k <= 0.474:
            num_children = 2
        for i in range(num_children):
            parent2 = random.sample(population, 1)
            k = random.uniform(0,1)
            child = crossover(parent1, parent2)
            child = mutate(child)
            newPopulation.append(child)
    population = newPopulation
    
def crossover(parent1, parent2):
    p1 = random.uniform(0, 1)
    if p1 <= 0.1:
        p2 = random.uniform(0, 1)

    else:
        return parent1

def mutate(child):
    return

def fitness(toolbox,world,situations):
    score = 0
    for situation in situations:
        if toolbox.get_action(situation) == world.get_action(situation) :
            score +=1
    return len(situations) - score

