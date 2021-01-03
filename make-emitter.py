from os import linesep
import sys

inputfile = sys.argv[1]
outputname = sys.argv[2]
fileout = open(outputname,'w')

fileobj = open(inputfile,'r')
lines = fileobj.readlines()
fileobj.close()

junctions = []

junc = False
emit = False
nl = len(lines)
for i in range(0,nl):
    ss=lines[i].split('\t')
    if (junc):
        if (len(ss)==1):
            junc = False
        else:
            if (ss[0][0] != ";"):
                # print(ss[0])
                junctions.append(ss[0])
    if (ss[0].find("JUNCTIONS") > -1):
        junc = True

emitters = []
for i in range(0,len(junctions)):
    emitters.append(junctions[i] + "\t" + '0' + "\n")

for i in range(0,nl):
    if (lines[i].find("EMITTERS") > -1):
        for j in range(0,len(emitters)):
            lines.insert(i+2, emitters[j])

for i in range(0,nl):
    fileout.write(lines[i])
fileout.close
