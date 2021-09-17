import sys
import subprocess
import random
import os
from datetime import datetime

inp_file = sys.argv[1]
pop_size = int(sys.argv[2])
generations = int(sys.argv[3])
ls = sys.argv[4]
casecount = int(sys.argv[5])
sensor_count = float(sys.argv[6])
csv_file = './try-results-' + ls + '/experiment-simple.csv'
pipe_weight = 'pipe_weight_' + ls + '.txt'

# sensor_count = int(sys.argv[6])

weight = open(pipe_weight, 'r')
result = 'results ' + str(pop_size) + ' ' + str(generations) + ' ' + ls + '.txt'

lines = []
results = []
leaks = []
final_results = [] #debug only
save_fitness = [] #debug only
simulation_dir = './temp'
correct = 0
incorrect = 0
junctions = []
pipes = []
cases = []
sensors = []

def place_sensor():
    lines = weight.readlines()
    for i in range(sensor_count):
        sensors.append(lines[i].split()[0])
    # for i in sensors:
    #     print (i)

def get_junctions():
    try:
        fileobj = open(inp_file,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print ('Input file error')
    
    global pipes
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
                        pipes.append(ss[0])
            if (ss[0].find("JUNCTIONS") > -1):
                junc = True
            if (ss[0].find("PIPES") > -1):
                pip = True

def create_species():
    temp = []
    for i in range(len(junctions)):
        gen = round(random.uniform(0,1),2)
        temp.append(gen)
    # print(len(temp))
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

def generate_temp():
    fileobj = open(inp_file,'r')
    lines = fileobj.readlines()
    fileobj.close()
    fileout = open('temp.inp','w')
    for i in range(len(lines)):
        # print(lines[i])
        fileout.write(lines[i])
    fileout.close()

def change(category, idname, pos,val):
    # print(idname)
    fileout = open('temp.inp','r+')
    lines = fileout.readlines()
    fileout.seek(0)
    fileout.truncate()

    incategory = False
    nl = len(lines)
    for i in range(nl):
        # print(lines[i])
        ss=lines[i].split()
        # print(type(ss))
        if (ss):
            # print(ss[0])
            if (incategory):
                
                if (len(ss) <= 1):
                    incategory = False
                else:
                    # print(ss[0])
                    if ((ss[0].find(str(idname)) > -1) or (str(idname)=='*' and ss[0][0]<>';')):
                        # print('ss')
                        ss[pos] = str(val)
                        ss.append('\n')
                        # print(ss)
                        lines[i] = '\t'.join(ss)
                        # print(lines[i])
                        # print(i)
            if (ss[0].find(category) > -1):
                incategory = True
        # print(lines[i])
        # print(i)
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
    generate_temp()
    fitness = 0.0
    # count = 0
    for i in range(len(species)):
        change('EMITTERS', str(junctions[i]), 1, species[i])
    subprocess.call(['java', '-cp', 'AwareEpanetNoDeps.jar', 'org.addition.epanet.EPATool', 'temp.inp'])
    species_flow = getflows('temp.inp.links.out')
    # print(species_flow)
    for i in range(len(flows)):
        if pipes[i] in sensors:
            # print (count)
            # count+=1
            fitness = fitness + abs(float(flows[i]) - float(species_flow[i]))
    return round(fitness, 2)

def mutate(chromosome):
    random_gen = random.randint(0,len(chromosome)) - 1
    random_value = round(random.uniform(0,1), 2)
    # print(chromosome)
    chromosome[random_gen] = round(((chromosome[random_gen] + random_value) % 1.00), 2)
    return chromosome

def crossover(parent1, parent2):
    cross_point = random.randint(0,len(parent1) - 1)
    # print("parent 1: " + str(parent1))
    # print("parent 2: " + str(parent2))
    child = parent1[:cross_point] + parent2[cross_point:]
    # print("child: " + str(child))
    child = mutate(child)
    return child

def GA(pop, flows):
    global save_fitness
    # print("Population: ")
    # for i in range(len(pop)):
    #     print(pop[i])
    fitness = []
    new_pop = []
    for i in range(len(pop)):
        # print(i)
        fitness.append(find_fitness(pop[i], flows))
    # print(fitness)
    # save_fitness.append(fitness)
    sorted_pop = [pop for _, pop in sorted(zip(fitness,pop))]
    # print("Sorted population: ")
    # for i in range(len(sorted_pop)):
    #     print(sorted_pop[i])
    for i in range(int(pop_size * 0.5)):  
        new_pop.append(sorted_pop[i])
    for i in range(int(pop_size * 0.25)):
        new_pop.append(crossover(sorted_pop[i],sorted_pop[random.randint(0,len(sorted_pop)-1)]))
    for i in range(int(pop_size * 0.25)):
        new_pop.append(create_species())

    return new_pop

def check_result(species, answer):
    global leaks
    global correct
    global incorrect
    species_copy = species[:]
    leak = []
    for i in range(int(len(junctions)/3)):
        biggest_leak = species_copy.index(max(species_copy))
        leak.append(junctions[biggest_leak])
        species_copy[biggest_leak] = 0.0
    leaks.append(leak)
    if (answer in leak):
        correct += 1
    else:
        incorrect +=1

def detect_leak(case):
    global final_results
    flows = []
    fitness = []
    case = case.split(',')
    population = initial_pop(pop_size)
    # for i in range(len(population)):
    #     print (population[i])
    for i in range(len(pipes)):
        flows.append(round(float(case[i+2]),2))
    for i in range(generations):
        population = GA(population, flows)
        # print(len(population))
    for i in range(len(population)):
        fitness.append(find_fitness(population[i], flows))
    sorted_pop = [population for _, population in sorted(zip(fitness, population))]
    # print(len(sorted_pop))
    final_results.append(sorted_pop[0])
    check_result(sorted_pop[0], case[1])
    return sorted_pop[0]

start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
get_junctions()
sensor_count = int(len(pipes)*sensor_count)
cases = get_cases()
place_sensor()
for i in range(casecount):
    case = random.randint(len(junctions),len(cases))
    lines.append(case)
    results.append(detect_leak(cases[case-1]))
end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
fileout = open(result, 'w')
fileout.write("Start time: " + start + " End time: " + end + '\n')
fileout.write("Test case = " + str(correct+incorrect) + "\n")
fileout.write("Correct prediction = " + str(correct) + "\n")
fileout.write("Incorrect prediction = " + str(incorrect) + '\n')
# for i in range(len(save_fitness)):
#     fileout.write(str(save_fitness[i]) + '\n')
for i in range(len(results)):
    fileout.write(str(lines[i]) + ' ' + str(leaks[i]) + ' ' + str(results[i]) + '\n')
# for i in range(len(cases)):
#     fileout.write(detect_leak(cases[i]))
fileout.close()
# os.remove("temp.inp")
# os.remove("temp.inp.links.out")
# os.remove("temp.inp.nodes.out")