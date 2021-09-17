import subprocess
import sys

inp_file = sys.argv[1]
# pop_size = sys.argv[2]
# generations = sys.argv[3]
casecount = sys.argv[2]

leaksizes = [0.2, 0.4, 0.6, 0.8]

# populations = [10, 20, 40, 80]
# generations = populations[:]

# subprocess.call("py -2 try.py " + inp_file + ' 0.5')
# subprocess.call("py -2 sensor-locate.py 0.5 " + inp_file)

# for i in populations:
#     for j in generations:
#         subprocess.call("py -2 find-leak.py " + inp_file + ' ' + str(i) + ' ' + str(j) + ' 0.5 10 1')

# subprocess.call(['java', '-cp', 'AwareEpanetNoDeps.jar', 'org.addition.epanet.EPATool', inp_file])

for i in leaksizes:
    subprocess.call("py -2 try.py " + inp_file + ' ' + str(i))
    subprocess.call('py -2 sensor-locate.py ' + str(i) + ' ' + inp_file)
    subprocess.call("py -2 find-leak.py " + inp_file + ' 10 80 ' + str(i) + ' ' + casecount + ' 1')