import sys


leaksize = sys.argv[1]
inp_file = sys.argv[2]
csv_file = 'try-results-' + leaksize +'/experiment-simple.csv'
output = 'pipe_weight_' + leaksize + '.txt'
pipes = []

def get_pipes():
    try:
        fileobj = open(inp_file,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print ('Input file error')
    
    pipes = []
    pip = False
    nl = len(lines)
    for i in range(nl):
        ss=lines[i].split()
        if (ss):
            if (pip):
                if (len(ss) <= 1):
                    pip = False
                else:
                    if (ss[0].find("ID") < 0):
                        pipes.append(ss[0])
            if (ss[0].find("PIPES") > -1):
                pip = True
    return pipes

def weight_pipes(pipes):
    try:
        fileobj = open(csv_file, 'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        print ('Csv file error')

    # print(lines[0])
    firstline = lines[0].split(',')
    weight = []
    difference = []
    for i in range(len(pipes)):
        weight.append(round(float(firstline[2+i]),2))
        difference.append(0)
    change = difference[:]
    lines = lines[9:]
    for line in lines:
        ss = line.split(',')
        for i in range(len(pipes)):
            variance = round(abs(weight[i] - float(ss[2+i])), 2)
            if variance != 0:
                change[i] = change[i] + 1
            difference[i] = difference[i] + variance
            difference[i] = round(difference[i], 2)

    sorted = zip(change, difference, pipes)
    sorted.sort(reverse = True)
    return sorted

# for i in range(len(weight)):
#     print(pipes[i] + ': ' +weight[i])


pipes = get_pipes()
result = weight_pipes(pipes)
fileout = open(output, 'w')
for i in result:
    # fileout.write(str(i[0]) + ' ' + str(i[1]) + ' ' + i[2])
    fileout.write(i[2])
    fileout.write('\n')
# for i in pipes:
#     print(i)