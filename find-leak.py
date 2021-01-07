import sys
import subprocess
import random
import os
import time

inp_file = sys.argv[1]
csv_file = sys.argv[2]
pop_size = int(sys.argv[3])
generations = int(sys.argv[4])
result = 'results.txt'

results = []
simulation_dir = './temp'
correct = 0
incorrect = 0
junctions = []
cases = []
pipe_count = 0

def get_junctions():
    try:
        fileobj = open(inp_file,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print ('Input file error')
    
    global pipe_count
    junc = False
    pip = False
    nl = len(lines)
    for i in range(nl):
        ss=lines[i].split()
        if (ss):
            if (junc):
                if (len(ss) <= 1):
                    junc = False
                else:
                    if (ss[0].find("ID") < 0):
                        junctions.append(ss[0])
            if (pip):
                if (len(ss) <= 1):
                    pip = False
                else:
                    if (ss[0].find("ID") < 0):
                        pipe_count += 1
            if (ss[0].find("JUNCTIONS") > -1):
                junc = True
            if (ss[0].find("PIPES") > -1):
                pip = True

def create_species():
    temp = []
    for i in range(len(junctions)):
        gen = round(random.uniform(0,1),2)
        temp.append(gen)
    return temp

def initial_pop(size):
    pop = []
    for i in range(size):
        pop.append(create_species())
    return pop

def get_cases():
    try:
        fileobj = open(csv_file,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print("CSV open error")
    return lines

def change(category, idname, pos,val):
    try:
        fileobj = open(inp_file,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print("inp file open error")
    try:
        fileout = open("temp.inp",'w')
    except:
        print("temp file open error")

    incategory = False
    nl = len(lines)
    for i in range(nl):
        ss=str(lines[i].split())
        if (ss):
            if (incategory):
                if (len(ss) <= 1):
                    incategory = False
                else:
                    if ((ss[0].find(idname) > -1) or (idname=='*' and ss[0][0]!=';')):
                        ss[pos] = val
                        lines[i] = '\t'.join(ss)
            if (ss[0].find(category) > -1):
                incategory = True
        fileout.write(lines[i])
    fileout.close()

def getflows(linkfile):
    try:
        fileobj = open(linkfile,'r')
        lines = fileobj.readlines()
        fileobj.close()
        # os.remove(fileobj)
    except:
        print("simulation file open error")
    nl = len(lines) - 2
    flows = range(0,nl)
    for i in range(len(flows)):
        ss = lines[i+2].split()
        flows[i] = ss[5]
    return flows

def find_fitness(species, flows):
    fitness = 0.0
    for i in range(len(species)):
        change('EMITTERS', i, 1, species[i])
    subprocess.call(['java', '-cp', 'AwareEpanetNoDeps.jar', 'org.addition.epanet.EPATool', 'temp.inp'])
    species_flow = getflows('temp.inp.links.out')
    for i in range(len(flows)):
        fitness = fitness + abs(float(flows[i]) - float(species_flow[i]))
    return round(fitness, 2)

def mutate(chromosome):
    random_gen = random.randint(0,len(chromosome)) - 1
    random_value = round(random.uniform(0,1), 2)
    # print(chromosome)
    chromosome[random_gen] = round(((chromosome[random_gen] + random_value) % 1.00), 2)
    return chromosome

def crossover(parent1, parent2):
    # print("parent 1: " + str(parent1))
    # print("parent 2: " + str(parent2))
    child = parent1[:pipe_count/2] + parent2[pipe_count/2:]
    # print("child: " + str(child))
    mutate(child)
    return child

def GA(pop, line):
    # print("Population: ")
    # for i in range(len(pop)):
    #     print(pop[i])
    flows = []
    fitness = []
    new_pop = []
    for i in range(pipe_count):
        flows.append(round(float(line[i+2]),2))
    for i in range(len(pop)):
        # print(i)
        fitness.append(find_fitness(pop[i], flows))
    sorted_pop = [pop for _, pop in sorted(zip(fitness,pop))]
    # print("Sorted population: ")
    # for i in range(len(sorted_pop)):
    #     print(sorted_pop[i])
    for i in range(int(pop_size * 0.75)):  
        new_pop.append(sorted_pop[i])
    for i in range(int(pop_size * 0.25)):
        new_pop.append(crossover(new_pop[i],new_pop[i + int(pop_size / 4)]))

    return new_pop

def check_result(species, answer):
    global correct
    global incorrect
    leak = []
    for i in range(3):
        biggest_leak = species.index(max(species))
        leak.append(junctions[biggest_leak])
        species[biggest_leak] = 0.0
    if (answer in leak):
        correct += 1
    else:
        incorrect +=1

def detect_leak(case):
    flows = []
    fitness = []
    case = case.split(',')
    population = initial_pop(pop_size)
    # for i in range(len(population)):
    #     print (population[i])
    for i in range(generations):
        population = GA(population, case)
        # print(len(population))
    for i in range(pipe_count):
        flows.append(round(float(case[i+2]),2))
    for i in range(len(population)):
        fitness.append(find_fitness)(population[i], flows)
    sorted_pop = [population for _, population in sorted(zip(fitness, population))]
    check_result(sorted_pop[0], case[1])
    return sorted_pop[0]

get_junctions()
cases = get_cases()
for i in range(len(cases)/4):
    results.append(detect_leak(cases[random.randint(9,len(cases))]))
fileout = open(result, 'w')
fileout.write("Test case = " + str(correct+incorrect))
fileout.write("Correct prediction = " + str(correct))
fileout.write("Incorrect prediction = " + str(incorrect))
for i in range(len(results)):
    fileout.write(str(results[i]))
# for i in range(len(cases)):
#     fileout.write(detect_leak(cases[i]))
fileout.close()
os.remove("temp.inp")
os.remove("temp.inp.links.out")
os.remove("temp.inp.nodes.out")