import sys

inputfile = sys.argv[1]

junctions = []
pipes = []

source = open(inputfile,'r')
lines = source.readlines()
source.close()

class Node:
    def __init__(self, type):
        self.type = type
        self.name = "NULL"
        self.source = []
        self.dest = []

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
            if not ss[0]:
                junc = False
            else:
                if (ss[0].find("ID") < 0):
                    if (ss[0][0] == " "):
                        junctions.append(ss[0][1:])
                    else:
                        junctions.append(ss[0])
        if (pip):
            if not ss[0]:
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

# for i in range(len(pipes)):
#     print("Pipe name: " + pipes[i].name)
#     print("Pipe source: " + pipes[i].source[0].name)
#     print("Pipe destination "  + pipes[i].dest[0].name)

# for i in range(len(junctions)):
#     print("Junction name: " + junctions[i].name)
#     print("Junctions sources: ")
#     for j in range(len(junctions[i].source)):
#         print (junctions[i].source[j].name)
#     print("Junctions destinations: ")
#     for j in range(len(junctions[i].dest)):
#         print (junctions[i].dest[j].name)