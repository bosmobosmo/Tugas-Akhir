import sys
import random

inputfile = sys.argv[1]
csv = './try-results/experiment-simple.csv' #modify according to simulator results directory
pop_size = int(sys.argv[2])

no_leak = []
junctions = []
pipes = []
populations = []

source = open(inputfile,'r')
lines = source.readlines()
source.close()

class Node:
    def __init__(self, type):
        self.type = type
        self.name = "NULL"
        self.source = []
        self.dest = []
        self.flow = 0.0

    def clear_downstream(self):
        if (self.type == "Junction"):
            if self.name not in no_leak:
                no_leak.append(self.name)
        for i in range(len(self.dest)):
            self.dest[i].clear_downstream()

    def clear_upstream(self):
        if (self.type == "Junction"):
            if self.name not in no_leak:
                no_leak.append(self.name)
        for i in range(len(self.source)):
            self.source[i].clear_upstream()

def make_junctions():
    junc_objs = [Node("Junction") for i in range(len(junctions))]
    for i in range(len(junctions)):
        junc_objs[i].name = str(junctions[i])
    return junc_objs

def make_junctions_connections():
    for i in range(len(junctions)):
        for j in range(len(pipes)):
            if (pipes[j].dest[0] == junctions[i]):
                junctions[i].source.append(pipes[j])
            if (pipes[j].source[0] == junctions[i]):
                junctions[i].dest.append(pipes[j])
    # for i in range(len(junctions)):
    #     if not junctions[i].source:
    #         junctions[i].source.append("NULL")
    #     if not junctions[i].dest:
    #         junctions[i].dest.append("NULL")

def make_pipes():
    pipe_objs = [Node("Pipe") for i in range(len(pipes))]
    for i in range(len(pipe_objs)):
        pipe_objs[i].name = pipes[i][0][1:]
        for j in range(len(junctions)):
            if (junctions[j].name == pipes[i][1]):
                pipe_objs[i].source.append(junctions[j])
            if (junctions[j].name == pipes[i][2]):
                pipe_objs[i].dest.append(junctions[j])
    return pipe_objs

def read_data():
    nl = len(lines)

    junc = False
    pip = False
    for i in range(0,nl):
        ss=lines[i].split('\t')
        if (junc):
            if (not ss[0] or ss[0] == '\n'):
                junc = False
            else:
                if (ss[0].find("ID") < 0):
                    if (ss[0][0] == " "):
                        junctions.append(ss[0][1:])
                    else:
                        junctions.append(ss[0])
        if (pip):
            if (not ss[0] or ss[0] == '\n'):
                pip = False
            else:
                if (ss[0].find("ID") <0):
                    pipe = []
                    pipe = ss[:3]
                    pipes.append(pipe)
        if (ss[0].find("JUNCTIONS") > -1 or ss[0].find("RESERVOIR") > -1):
            junc = True
        if (ss[0].find("PIPES") > -1):
            pip = True

def get_flow():
    source = open('./try-results/experiment-simple.csv') 
    lines = source.readlines()
    source.close()

    ss = lines[0].split(',')
    for i in range(len(pipes)):
        pipes[i].flow = ss[i+4]
        
# def init_pop():
#     # print(len(pipes))
#     spec = []
#     for i in range(200):
#         del spec [:]
#         for j in range(len(pipes)):
#             spec.append(random.randint(0,1))
#         # print(spec)
#         # print("append")
#         populations.append(spec[:])

def detect_leak(chromosome, line):
    # print(chromosome)
    # print(line)
    leak = []
    for i in range(len(junctions)):
        leak.append(junctions[i].name)
    del no_leak[:]
    # print (no_leak)
    for i in range(len(chromosome)):
        if (chromosome[i] == 1) :
            # print(i)
            # print(line[i+4])
            if (line[i+4] == pipes[i].flow):
                # print(str(i) +' '+ str(line[i+4]) + ' '+ pipes[i].flow)
                pipes[i].clear_downstream()
            else:
                pipes[i].clear_upstream()
    # print(no_leak)
    for i in range(len(no_leak)):
        leak.remove(no_leak[i])
    # print(leak)
    return leak

def leak_count(pair):
    return len(pair[0])

def fitness(pop, line):
    # print(pop)
    # print(line[1])
    leak = []
    new_pop = []
    for i in range(len(pop)):
        # print(i)
        leak.append(detect_leak(pop[i], line))
    # print (len(pop))
    # print (len(leak))
    sorted_pop = [pop for _, pop in sorted(zip(leak,pop), key=leak_count)]
    for i in range(len(sorted_pop)):
        # for x in range(len(leak[i])):
        #     print(leak[i][x])
        if (line[1] in leak[i]):
            new_pop.append(sorted_pop[i])
    # for i in range(len(pop)):
    #     if (pop[i] not in new_pop):
    #         new_pop.append(pop[i])
    # if (len(new_pop)< 200):
    #     print(len(new_pop))
    # if (len(new_pop) <10 and len(new_pop) > 0):
    #     for i in range(len(new_pop)):
    #         print new_pop[i]
    return new_pop

def create_chromosome():
    spec = []
    for j in range(len(pipes)):
        spec.append(random.randint(0,1))
    return spec

def sensor_count(chromosome):
    count = 0
    for i in range(len(chromosome)):
        if chromosome[i] == 1:
            count+=1
    return count

def cross(parents):
    children = []
    parent_count = len(parents)
    for i in range(parent_count/2):
        children.append(parents[i][:10] + parents[i+(parent_count/2)][10:])
    return children

def mutate(pop):
    for i in range(len(pop)):
        for x in range(len(pop[i])):
            if(random.randint(0,3) == 3):
                pop[i][x] = (pop[i][x] + 1) %2
    return pop

def GA(pop):
    source = open(csv)
    lines = source.readlines()
    source.close()
    new_pop = []
    # print(len(lines))

    for i in range(len(lines)-9):
        if (len(pop) <= 1):
            print(i)
        # if (len(pop) < 200):
        #     print ("line: " + str(i))
        children = []
        line = lines[i+9].split(',')
        # print(len(pop))
        # print (i)
        # for i in range(len(pop)):
        #     print (pop[i])
        new_pop = fitness(pop, line)
        # print (len(new_pop))
        new_pop.sort(key=sensor_count)
        if(len(new_pop) < len(pop)):
            for i in range(len(pop) - len(new_pop)):
                new_pop.append(create_chromosome())
        parents = new_pop[:(len(new_pop)/2)]
        del new_pop[len(new_pop)*3/4:]
        children = cross(parents)
        children = mutate(children)
        # print("parent count: " + str(len(parents)))
        # print("pop count: " + str(len(pop)))

        pop = []
        pop.extend(new_pop)
        pop.extend(children)
        # print(len(pop))
        # for i in range(len(pop)):
        #     print(pop[i])

    return pop[0]
    # for i in range(len(parents)):    
    #     print(parents[i])
        
    # print (len(pop))
    # for i in range(len(pop)):
    #     print(pop[i])
    # print ('\n')
    
    # for i in range(len(new_pop)):
    #     print (new_pop[i])

read_data()

# print ("PIPES:")
# for i in range(len(pipes)):
#     print (pipes[i])
# print ("JUNCTIONS:")
# for i in range(len(junctions)):
#     print (junctions[i])

junctions = make_junctions()
pipes = make_pipes()
make_junctions_connections()
get_flow()
# init_pop()
for i in range(pop_size):
    populations.append(create_chromosome())
# for i in range(len(populations)):
#     print(populations[i])
best = GA(populations)
print(best)
for i in range(len(best)):
    if (best[i] == 1):
        print(pipes[i].name)
# pipes[4].clear_upstream()

# for i in range(len(no_leak)):
#     print no_leak[i]

# for i in range(len(pipes)):
#     print("Pipe name: " + pipes[i].name)
#     print("Pipe source: " + pipes[i].source[0].name)
#     print("Pipe destination "  + pipes[i].dest[0].name)
#     print("Flow :" + pipes[i].flow)

# for i in range(len(junctions)):
#     print("Junction name: " + junctions[i].name)
#     print("Junctions sources: ")
#     for j in range(len(junctions[i].source)):
#         print (junctions[i].source[j].name)
#     print("Junctions destinations: ")
#     for j in range(len(junctions[i].dest)):
#         print (junctions[i].dest[j].name)

