from os import linesep
from os import mkdir
import os.path
import sys
import subprocess
import time
import random

inputfile = sys.argv[1]
leaksize = sys.argv[2]
experimentname = 'experiment-simple'
if not os.path.isdir('./try-results-' + leaksize + '/'):
    mkdir("./try-results-" + leaksize + "/")
resultsdir = "./try-results-" + leaksize +"/"
databasedir = "./try-results-" + leaksize + "/"
databasename = experimentname+'.csv'

ls = float(leaksize)
ecrange = [ls-0.02, ls+0.02]
junctions = []
leakindices = []
roughnessavg = 0.25
repeats = 10

start = time.time()

def get_junctions():
    try:
        fileobj = open(inputfile,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print ('Input file error')
    
    global junctions
    # global pipes
    junc = False
    # pip = False
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
            # if (pip):
            #     if (len(ss) <= 1):
            #         pip = False
            #     else:
            #         if (ss[0].find("ID") < 0):
            #             pipes.append(ss[0])
            if (ss[0].find("JUNCTIONS") > -1):
                junc = True
            # if (ss[0].find("PIPES") > -1):
            #     pip = True

def variationRange(n1, n2):
    return round(random.uniform(n1,n2),2)

def change(inputfile, outputfile, category, idname, pos, val):
    try:
        fileobj = open(inputfile,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print 'Input file open error'
    try:
        fileout = open(outputfile,'w')
    except:
        print ' Output file open error'

    incategory = False
    nl = len(lines)
    for i in range(0,nl):
        ss=lines[i].split('\t')
        if (incategory):
            if (len(ss)==1):
                incategory = False
            else:
                if ((ss[0].find(idname) > -1) or (idname=='*' and ss[0][0]<>';')):
                    ss[pos] = val
                    sep = "\t"
                    lines[i] = sep.join(ss)
                    # print lines
        if (ss[0].find(category) > -1):
            incategory = True
        fileout.write(lines[i])
    fileout.close()


def getflows(linkfile):
    try:
        fileobj = open(linkfile, 'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print 'Link file open error'
    nl = len(lines)
    np = nl-2
    flows = range(0,np)
    for i in range(0,np):
        ss = lines[i+2].split('\t')
        flows[i] = ss[5]
    return flows

def getpressures(nodefile):
    try:
        fileobj = open(nodefile,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print 'Node file open error'
    nl = len(lines)
    np = nl-2
    pressures = range(0,np)
    for i in range(0,np):
        ss= lines[i+2].split('\t')
        pressures[i] = ss[4]
    return pressures

def getdemands(nodefile):
    try:
        fileobj = open(nodefile,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print 'Node file open error'
    nl = len(lines)
    np = nl-2
    demands = range(0,np)
    for i in range(0,np):
        ss = lines[i+2].split('\t')
        demands[i] = ss[6].replace("\n","")
    return demands

try:
    databasefile = open(databasedir+ databasename,'w')
except:
    print 'Database file open error'

get_junctions()

for r in range(0,repeats):
    for l in range(0,len(junctions)):
        rp = str(roughnessavg)
        fid=1
        lp = junctions[l]
        if r == 0:
            ec = str(0.0)
        else:
            ec = str(variationRange(ecrange[0],ecrange[1]))

        finaloutputfile = resultsdir+ 'tmpXX-EC-'+ec+'-LP-'+lp.rstrip().lstrip()+'-rp-'+rp+'-r-'+str(r)+'.inp'
        change(inputfile,finaloutputfile,'EMITTERS',lp, 1, ec)
        print 'Created: ',finaloutputfile

        subprocess.call(['java', '-cp', 'AwareEpanetNoDeps.jar', 'org.addition.epanet.EPATool', finaloutputfile])

        flows = getflows(finaloutputfile+'.links.out')
        pressure = getpressures(finaloutputfile+'.nodes.out')
        demands = getdemands(finaloutputfile+'.nodes.out')

        # lf = demands[leakindices[l]]
        opparams = [ec,lp]
        sep = ","
        csvobs = sep.join(opparams+flows+pressure+demands)
        databasefile.write(csvobs+'\n')
databasefile.close()
# end = time.time()
# elapsed = end - start
# print 'Finished in :' + str(elapsed) + ' seconds'



