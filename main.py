import random
from toolbox import ToolBox, Tree, ActionNode, CueNode
import matplotlib.pyplot as plt
import time

def crossover(parent1, parent2):
    p1 = random.uniform(0, 1)
    if p1 <= 0.1:
        p2 = random.uniform(0, 1)
        if p2 <= 0.5:
            c1 = random.randint(0, len(parent1.trees)-1)
            c2 = random.randint(0, len(parent2.trees)-1)
            parent1.trees[c1] = parent2.trees[c2]
            return parent1
        else:
            for h1, h2 in zip(parent1.trees, parent2.trees):
                node1 = h1.random_traverse()
                node2 = h2.random_traverse()
                node1.left_child = node2
                node2.parent = node1
            return parent1
    else:
        return parent1
    
def mutate(child):
    copyList = child.trees.copy()
    for i in range(len(child.trees)):
        if len(copyList) < len(child.trees):
            break
        p1 = random.uniform(0,1)
        if p1 <= 0.11:
            p2 = random.uniform(0,1)
            if p2 < 0.25:
                # Change selector cue 
                n = random.randint(0, SITUATION_AMOUNT-1)
                copyList[i].situation_index = n
            elif p2 < 0.50:
                # insert new selector and heuristic
                copyList.insert(i+1, Tree(DEPTH, ACTIONS, SITUATION_AMOUNT))
            elif p2 < 0.75:
                # Delete selector cue
                if len(copyList) > 1:
                    del copyList[i]
            else:
                # swap two selector cues
                j = random.randint(0,len(child.trees)-1)
                tmp = copyList[i]
                copyList[i] = copyList[j]
                copyList[j] = tmp
    child.trees = copyList

    for i, heuristic in enumerate(child.trees):
        print(i)
        current = heuristic.root.left_child
        while not isinstance(current, ActionNode):
            #heuristic.show()
            #time.sleep(0.01)
            if current is None:
                break
            p1 = random.uniform(0,1)
            if p1 <=0.11:
                p2 = random.uniform(0,1)
                if p2 <= 0.2:
                    print("change cue")
                    # change the curent situation index
                    n = random.randint(0, SITUATION_AMOUNT-1)
                    current.situation_index = n
                elif p2 <= 0.4: 
                    # change an action
                    print("change action")
                    n = random.choice(ACTIONS)
                    current.right_child.action = n
                elif p2 <= 0.6:
                    print("add cue")
                    current = heuristic.add_cue_action_pair(current)
                elif p2 <= 0.8:
                    print("delete cue")
                    # delete the current node
                    current = heuristic.delete_node(current)
                else:
                    print("swap cue")
                    # swap curent node with a random node
                    other = heuristic.random_traverse()
                    print(str(other), str(current))
                    if not isinstance(other, ActionNode) and other != current:
                        heuristic.swap_nodes(current, other)
                    current = other
            current = current.left_child
    return child
    

def fitness(toolbox,world,situations):
    score = 0
    for situation in situations:
        if toolbox.get_action(situation) == world.get_action(situation):
            score +=1
    return len(situations) - score # number of incorrect actions

# DEFINE GLOBAL CONSTANTS
p = 0.5 
DEPTH = 3
ACTIONS = range(1,5)
SITUATION_AMOUNT = 3

def run_simulation(depth = DEPTH, actions = ACTIONS, situation_amount = SITUATION_AMOUNT):
    populations = []
    # Startt the main evolution algorithm
    world = ToolBox(depth= depth, actions= actions, situation_amount= situation_amount)    
    population = [ToolBox(depth= depth, actions= actions, situation_amount= situation_amount) for _ in range(500)]
    count = 0
    while 0 < len(population) < 600:
        print("iteration: ", count)
        count += 1
        situations = [[random.choice([True,False]) for _ in range(10)] for _ in range(1000)]
        for i, individual in enumerate(population): # remove underperforming individuals
            print("induvidual: ", i)
            num_incorrect = fitness(individual, world, situations) 
            d = (1 - p)**num_incorrect
            k = random.uniform(0, 1)
            if k > d:
                population.remove(individual)
        print('Killed unperformers')
        newPopulation = []
        for individual in population: # choose two parents, choose num of children, crossover & mutate heuristics for children
            parent1 = individual
            num_children = 1
            k = random.uniform(0, 1)
            if k <= 0.474:
                num_children = 2
            print(time.time(), 'It reaches this for loop')
            for j in range(num_children):
                #print("mutating: ", j)
                parent2 = random.choice(population)
                if parent2 == parent1:
                    continue
                #print(type(parent2), parent2)
                child = crossover(parent1, parent2)
                #print("done crosover: ", type(child))
                child = mutate(child)
                #print("done mutating: ", type(child))
                newPopulation.append(child)
        population = newPopulation
        populations.append(len(population)) 
    return populations

def main():
    data = run_simulation()
    plt.plot(data)
    plt.xlabel('Generation')
    plt.ylabel('Population')
    plt.show()

if __name__ == '__main__':
    main()