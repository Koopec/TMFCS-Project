from random import choice, random, randrange, sample, randint
from copy import deepcopy
from itertools import zip_longest
# from etaprogress.progress import ProgressBar, XOfY, Bar, ETA


from sys import argv
from math import ceil
import matplotlib.pyplot as plt

try:
    range = xrange
except NameError:
    pass

# Constant parameters for simulation
K_size = 10#20#50
nactions = 50
NSELECTED = 200
NPOPULATION = 200
ENDGAME = 500
KTRIES = 200#1000#200
WBT_SIZE = 5
WBT_HEURISTIC_SIZE = 5
NTOURNAMENT = 5
POINT_MUTATION = 0.11
MAX_SIZE = 30
P_DEATH = 0.0004052120601755858838
P_SURVIVAL = 1 - P_DEATH

cues = [lambda K, i=i: K[i] for i in range(K_size)] + [lambda K, i=i, neg=True: not K[i] for i in range(K_size)]
pieces_of_knowledge = {}

for i in range(K_size):
    s = {cues[i], cues[i + K_size]}
    pieces_of_knowledge[cues[i]] = s
    pieces_of_knowledge[cues[i + K_size]] = s
actions = range(nactions)

def s2c(c):
	if type(c) == str:
		i = int(c[2])
		if c[0] == '¬':
			i += K_size
		c = list(cues)[i]
	return c

# Evaluating a toolbox in a certain situation returns the action that toolbox associates with that situation
def eval_toolbox(t, K):
    for c, h in t:
        c = s2c(c)
        if c(K):
            return eval_heuristic(h, K)
    return eval_heuristic(t[0][1], K)


def eval_heuristic(h, K):
    for c, a in h:
        c = s2c(c)
        if c(K):
            return a
    return h[-1][1]


def time_to_eval_toolbox(t, K):
    for i, (c, h) in enumerate(t):
        if c(K):
            return time_to_eval_heuristic(h, K) + i
    return time_to_eval_heuristic(t[0][1], K) + len(t) - 1


def time_to_eval_heuristic(h, K):
    for i, (c, a) in enumerate(h):
        if c(K):
            return i
    return len(h) - 1


# Given two toolboxes and a situation, do both toolboxes in that situation evaluate to the same action?
def same_action(t1, t2, K):
    return eval_toolbox(t1, K) == eval_toolbox(t2, K)


_t_mutations = ['insert', 'delete', 'change cue', 'swap']
_h_mutations = ['insert', 'delete', 'change cue', 'change action', 'swap']
def _mutation_selector(t):
    t = deepcopy(t) # make a copy of the original toolbox, to prevent double mutation when a single toolbox is selected twice
    for i, (c, h) in enumerate(t):
        if chance(POINT_MUTATION):
            mut = choice(_t_mutations)
            #print('selector', mut)
            if mut == 'insert':
                if toolbox_size(t) < MAX_SIZE:
                    t.insert(i, (choice(cues), [(choice(cues), choice(actions))]))
            elif mut == 'delete':
                if len(t) > 1:
                    t.pop(i)
            elif mut == 'change cue':
                t[i] = (choice(cues), h)
            elif mut == 'swap':
                j = randrange(len(t))
                t[i], t[j] = t[j], t[i]
    return t


def _mutation_heuristic(t, h):
    for i, (c, a) in enumerate(h):
        if chance(POINT_MUTATION):
            mut = choice(_h_mutations)
            if mut == 'insert':
                if toolbox_size(t) < MAX_SIZE:
                    h.insert(i, (choice(cues), choice(actions)))
            elif mut == 'delete':
                if len(h) > 1:
                    h.pop(i)
            elif mut == 'change cue':
                h[i] = (choice(cues), a)
            elif mut == 'change action':
                h[i] = (c, choice(actions))
            elif mut == 'swap':
                j = randrange(len(h))
                h[i], h[j] = h[j], h[i]


def mutate(t):
    t = _mutation_selector(t)
    for c, h in t:
        _mutation_heuristic(t, h)
    return t


def _crossover(t1, t2):
    i1 = randrange(len(t1))
    i2 = randrange(len(t2))
    return t1[:i1] + t2[i2:]


def _crossover2(t1, t2):
    for (c1, h1), (c2, h2) in zip(t1, t2):
        yield choice([c1, c2]), _crossover(h1, h2)
    if chance(.5):
        for item in t1[len(t2):]:
            yield item
        for item in t2[len(t1):]:
            yield item


def crossover(t1, t2):
    if chance(.1):
        if chance(.5):
            return _crossover(t1, t2)
        else:
            return list(_crossover2(t1, t2))
    else:
        return t1


# helper function that returns true with a chance of p
def chance(p):
    return random() < p


# the score of a toolbox is the fraction of situations where it evaluates to the same action as the world
def score(t, world, situations):
    return sum(1.0 for K in situations if same_action(t, world, K)) / len(situations)


def time_to_action(t, situations):
    return sum(0.05 * time_to_eval_toolbox(t, K) for K in situations) / len(situations)


def toolbox_size(t):
    return sum(len(h) for c, h in t)


def fitness_by_size(t):
    return toolbox_size(t) * .00002


# the fitness consists of the score subtracted by the fitness by size
def fitness(t, world, situations):
    return score(t, world, situations) #- fitness_by_size(t)


# tournament selection in which the best of 10 is chosen
def select_parent(generation):
    return generation[max(sample(range(NPOPULATION), NTOURNAMENT))]


# prepares the selection by choosing a list of situations
# and sorting the generation, with the best at the end
def selection_phase(generation, world, recording, i, fdr):
    situations = [[chance(.5) for _ in range(K_size)] for _ in range(KTRIES)]		# What changes if chance level for cues is changed?
    generation.sort(key=lambda t: fitness(t, world, situations))
    #recording.append((fitness(generation[-1], world, situations), fitness(generation[0], world, situations), sum(fitness(toolbox, world, situations) for toolbox in generation)/len(generation), fitness(generation[len(generation) // 2], world, situations)))
    if rec_distribution(i):
        ind = range(21)
        bins = [0] * 21
        for t in generation:
            fit = fitness(t, world, situations)
            bins[ceil(fit * 20)] += 1
            #plt.clear()
        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, bins, 0.1)
        plt.savefig('resultaten/dist_varpop_{}_{}.png'.format(name, i))
        plt.close()
        print(','.join(str(x) for x in bins), file=fdr)
    return [t for t in generation if chance(P_SURVIVAL ** (len(situations) - sum(1.0 for K in situations if same_action(t, world, K))))]

# selects parents from the old generation, performs cross-over and mutation
# and returns the new generation
def variation_phase(generation):
    for p in generation:
        for _ in range(choice((1, 1, 1, 1, 1, 2))):
            yield mutate(crossover(p, choice(generation)))

best_change = False
last_best = None
def next_generation(generation, world, recording, i, ftb, fdr):
    global last_best, best_change
    generation = selection_phase(generation, world, recording, i, fdr)
    recording.append(str(len(generation)))
    best_change = False
    if rec(i) and generation and generation[-1] != last_best:
        last_best = generation[-1]
        best_change = True
        print('best of generation {}:'.format(i), file=ftb)
        pretty_print_toolbox(generation[-1], ftb)
    return list(variation_phase(generation))


# returns a random toolbox with fixed dimensions to be used as a world
# the world has these properties:
# * the selector chooses between WBT_SIZE heuristics
# * each heuristic consists of WBT_HEURISTIC_SIZE - 1 cues and WBT_HEURISTIC_SIZE actions	    # Doesnt actually assign more actions than cues!# * cues and actions are chosen at random with replacements
def world_building_toolbox():
    return [(choice(cues), [(choice(cues), choice(actions)) for _ in range(WBT_HEURISTIC_SIZE)]) for _ in range(WBT_SIZE)]

def generate_world_heuristic_item(cues_left):
    c = choice(list(cues_left))
    cues_left -= pieces_of_knowledge[c]
    return c, choice(actions)


def generate_world_heuristic(cues_left):
    c = choice(list(cues_left))
    cues_left -= pieces_of_knowledge[c]
    cues_left = cues_left.copy()
    return c, [generate_world_heuristic_item(cues_left) for _ in range(WBT_HEURISTIC_SIZE)]

def world_building_toolbox():
    cues_left = set(cues)
    return [generate_world_heuristic(cues_left) for _ in range(WBT_SIZE)]

# this generates a simple toolbox, containing only a single heuristic, which always results in the same action
# these are used in the first generation, to provide a start for the toolbox to evolve
def primitive_toolbox():
    return [(choice(cues), [(choice(cues), choice(actions)) for _ in range(randrange(1, 4))]) for _ in range(3)]

def pretty_print_cue(c):
    return '{}c{}'.format('¬' if len(c.__defaults__) > 1 else ' ', c.__defaults__[0])

def pretty_print_toolbox(t, ftb):
    print('   '.join('{:<4}    '.format(pretty_print_cue(c)) for c, h in t), file=ftb)
    for hs in zip_longest(*[h for c, h in t]):
        print('   '.join('{c:<4} a{a:<2}'.format(c=pretty_print_cue(i[0]), a=i[1]) if i else '        ' for i in hs), file=ftb)

def rec(i):
       return True
#    return i % 10 == 9

def rec_distribution(i):
    return True
#    return i % 50 == 49
def evolve():
    global name
    world = world_building_toolbox()
    #pretty_print_toolbox(world)
    generation = [primitive_toolbox() for _ in range(NPOPULATION)]
    best_fitness = []
    best_score = []
    mean_fitness = []
    mean_score = []
    recording = []
    name = argv[1] if len(argv) > 1 else 'results'
    ngen = int(argv[2]) if len(argv) > 2 else 1000
    ilist = []
    bestlist = []
    worstlist = []
    meanlist = []
    medianlist = []
    try:
        ftb = open('resultaten/toolbox_varpop_{}.txt'.format(name), 'w')
        fr = open('resultaten/ga_varpop_{}.csv'.format(name), 'w')
        fdr = open('resultaten/ga_distr_varpop_{}.csv'.format(name), 'w')
        print('world:', file=ftb)
        pretty_print_toolbox(world, ftb)
        print('gen_size', file=fr)
        #ProgressBar(range(ngen), widgets=[XOfY, ' ', Bar, ' ', ETA]):
        for i in range(ngen):
            generation = next_generation(generation, world, recording, i, ftb, fdr)
            print(i)
            if not generation or len(generation) >= ENDGAME:
                print('ENDGAME', len(generation))
                break
    finally:
        print('\n'.join(recording), file=fr)
        plt.plot(ilist, bestlist, 'b')
        plt.plot(ilist, worstlist, 'r')
        plt.plot(ilist, meanlist, 'y')
        plt.plot(ilist, medianlist, 'g')
        plt.savefig('resultaten/plot_fitness_varpop_{}.png'.format(name))
        plt.close()
        ftb.close()
        fr.close()
        fdr.close()

if __name__ == '__main__':
    evolve()
