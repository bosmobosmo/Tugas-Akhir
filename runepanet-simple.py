#/usr/bin/env python
#modify given EPAnet input file (sys.argv[1]) 
#by changing CATEGORY, ID to POS, VAL 
#and write result to output file 

# python help: http://www.tutorialspoint.com/python/ and https://docs.python.org/2/

from os import linesep
import sys
import subprocess
import random 
import time


# ##============================================
# ## Experiment 6 NEW: Simplest network to test: all known, 
# night flow and DMA - everything known and fixed
# run as python runepanet-simple.py ../issnip-examples/master-simple.inp   9 nodes * 100 repeats = 450 cases
# inputfile = sys.argv[1] #master file for EPAnet #PandL-DMA.inp
#time_start = time.time()
inputfile = './master-simple.inp'
experimentname = 'experiment-simple-012015' #used for output file and csv database
resultsdir = './results/' #where the results go XX cases
databasedir = './results/'
databasename = experimentname+'.csv'
# ## OPERATIONAL PROFILE TO BE TESTED 
ecrange = [0,0.5] #range of leak ec: ec=0.5 is 2.2 L/s at node 5 and 1.0 is 4.43 L/s=15000 phour
leakpositions = ['1 ','2 ','3 ','4 ','5 ','6 ','7 ','9 ','8 '] #no leaks at demand nodes though
leakindices = [0,1,2,3,4,5,6,7,8] #position of leak node in .nodes.inp columns (starting at 0)
#rationale: Karratha hourly peak = 140 L/h/hh night = 25 L/h/hh avg = apx 60 L/h/hh so take 1/3 of avg 22.5,15,30
#node name, lower and upper bound on demand for this node
demandvariation = [] #NONE 
#apx 10% variation from nodes 9d and 11s
roughnessavg = 0.25 #avg pipe fixed
#roughnessvariation = 0.1 #allow 10% variation none for this experiment
repeats = 100


start = time.time()

#n is the central value, p is a percentage eg 0.05 5%, 0.1 10%
#returns random in range n plus or minus p percent as a 2DP float
def variationPpct(n,p):
	pminus = 1.0 - p
	pplus = 1.0 + p
	return round(n*random.uniform(pminus,pplus),2)

#n1 to n2 is range for the variable - choose a random var from tis range 
#returns random in range n1,n2 as a 2DP float
def variationRange(n1,n2):
	return round(random.uniform(n1,n2),2)

##takes an input file, changes the give category and writes a new output file
def change(inputfile,outputfile,category,idname,pos,val):
	try:
		fileobj = open(inputfile,'r')
		lines = fileobj.readlines()
		fileobj.close()
	except:
		print 'Input file open error'
	try:
		fileout = open(outputfile,'w')
	except:
		print 'Output file open error '
		
	incategory = False
	nl = len(lines)
	for i in range(0,nl):
		#print lines[i]
		ss=lines[i].split('\t') #extract fields from tab separated input string
		#print ss
		if (incategory):
			#print 'length=',len(ss),ss
			if (len(ss)==1): #end of block
				incategory = False #close once done
				#print "category off ",lines[i]  
			else:
				if ((ss[0].find(idname) > -1) or (idname=='*' and ss[0][0]<>';')): #ignore header row
					#print "found id ",idname,' IN ',ss 
					ss[pos] = val
					sep="\t"
					lines[i] = sep.join(ss)
					#print 'make: ',lines[i]
					#print "---"
		if (ss[0].find(category) > -1):  #then start looking for line(s) to modify   
			#print "category on ",lines[i]         		
			incategory = True
		fileout.write(lines[i])
	fileout.close()
#end of change method


#get links information

def getflows(linkfile):
	try:
		fileobj = open(linkfile,'r')
		lines = fileobj.readlines()
		fileobj.close()
	except:
		print 'Link file open error'
	nl = len(lines) 
	np = nl-2 #number of pipes
	flows = range(0,np) #space for the flow values
	for i in range(0,np): #get
		ss = lines[i+2].split('\t')
		flows[i] = ss[5] #string array
	#print 'flows=',flows
	return flows
#test getlinks
#getlinks('../experiment1/tmp-EC-0.00-LP-6-RP-0.5.inp.links.out')
#quit()

#get pressure information
def getpressures(nodefile):
	try:
		fileobj = open(nodefile,'r')
		lines = fileobj.readlines()
		fileobj.close()
	except:
		print 'Node file open error'
	nl = len(lines) 
	np = nl-2 #number of pipes
	pressures = range(0,np) #space for the flow values
	for i in range(0,np): #get
		ss = lines[i+2].split('\t')
		pressures[i] = ss[4] #string array
	#print 'flows=',flows
	return pressures

#get simulated demands information
def getdemands(nodefile):
	try:
		fileobj = open(nodefile,'r')
		lines = fileobj.readlines()
		fileobj.close()
	except:
		print 'Node file open error'
	nl = len(lines) 
	np = nl-2 #number of pipes
	demands = range(0,np) #space for the flow values
	for i in range(0,np): #get
		ss = lines[i+2].split('\t')
		demands[i] = ss[6].replace("\n","") #last element in table to string array
	#print 'demands =',demands
	return demands

#main: generate all test files
#step 0. make a database file for results
try:
#	databasefile = open(resultsdir+ databasename,'w')
	databasefile = open(databasedir+ databasename,'w')
except:
	print 'Database file open error '
#step 1. run the simulation experiments	and record results 9 x 100 = 900
for r in range(0,repeats): #multiple cases
	for l in range(0,len(leakpositions)): #number of possible leak positions
		rp = str(roughnessavg) #same for all pipes
		#OR TODO roughness variation per pipe
		#rp = str(variationPpct(roughnessavg,roughnessvariation))
		#change(inputfile,'tmp1.inp','PIPES' ,'*', 5, rp+'\t') #TODO vary roughness in every pipe
		#change(inputfile,'tmp1.inp','PIPES' ,'*', 5, rp+'\t')
		fid=1 #file id
		# infilename = 'tmp1.inp'		
# 		for row in demandvariation: #number of demands to vary - one at a time
# 			fid=fid+1
# 			outfilename='tmp'+str(fid)+'.inp'
# 			demnode = row[0]
# 			demval = str(variationRange(row[1],row[2]))
# 			#print [row, demval]
# 			change(infilename,outfilename,'JUNCTIONS', demnode, 2, demval) #vary demand (col 2)
# 			infilename = outfilename #for next time

		#choose leak position (string name of node)
		lp = leakpositions[l] ## more than one positions ?? TODO RETURN HERE TO HAVE MULTI LEAKS
		#choose emitter cooefficient
		if r == 0: #make sure you have some 0 cases
			ec = str(0.48)
		else:
			ec = str(variationRange(ecrange[0],ecrange[1])) #find random value in ec range
			
		finaloutputfile = resultsdir+ 'tmpXX-EC-'+ec+'-LP-'+lp.rstrip().lstrip()+'-rp-'+rp+'-r-'+str(r)+'.inp'
		change(inputfile,finaloutputfile,'EMITTERS' , lp, 1, ec+'\r\n')  
		print 'Created: ',finaloutputfile

			#step 2: run epanet simulation
		subprocess.call(['java', '-cp', 'AwareEpanetNoDeps.jar', 'org.addition.epanet.EPATool', finaloutputfile]) ##didnt work ">>2", "../experiment1/log.txt"])
		
		#the process above will create .nodes.out and .links.out file, and are then used for the following process
		
		#step 3: get flow and pressure and demand results from output files and write to DB
		flows = getflows(finaloutputfile+'.links.out') #
		#print 'flows=',flows
		pressures = getpressures(finaloutputfile+'.nodes.out') #+'.nodes.out'
		#print 'pressures=',pressures
		demands = getdemands(finaloutputfile+'.nodes.out') #
			#print 'demands=',demands
		lf = demands[leakindices[l]] #look up leakflow given as a demand
		opparams=[ec,lp,lf,rp]
		sep=", "
		csvobs = sep.join(opparams+flows+pressures+demands)
			#print csvobs
		databasefile.write(csvobs+'\n')
databasefile.close()
end = time.time()
elapsed = end - start		
print 'Finished in : ' + str(elapsed) + ' seconds'


### NOTES
			#step 1: generate input file for simulation
			
			#vary roughness and demands each run at random
			
## experiment 6new


# # Jon exp3 only - but note this amount of demand variation masks leaks 
# 			d5 = str(variationPpct(userdemands[0],0.01)) #demands at nodes 5,9,11 alter by 1% only
# 			d9 = str(variationPpct(userdemands[1],0.01))
# 			d11 = str(variationPpct(userdemands[2],0.01))
# Jon exp4 only - big variation but observe demands as well
# QUESTION ?? should demands be linked eg nightflow low everywhere or random
# 			d5 = str(variationRange(lowdemand[0],highdemand[0])) #demands at nodes 5,9,11 alter by 1% only
# 			d9 = str(variationRange(lowdemand[1],highdemand[1]))
# 			d11 = str(variationRange(lowdemand[2],highdemand[2]))
# Jon exp5 only - nightflow
# #rationale Karratha peak = 140 L/h/hh avg = 60 L/h/hh nightmin = 25 L/h/hh with plusminus 2.5 which is 10%
# 			d5 = str(variationPpct(nightdemands[0],demandvariation)) 
# 			d9 = str(variationPpct(nightdemands[1],demandvariation))
# 			d11 = str(variationPpct(nightdemands[2],demandvariation))
#Jon exp 6 only - single inflow (pipe 19) and single outflow (new pipe 20) and demand only 12 L/s at node 5
			#d5 = str(variationPpct(nightdemands[0],demandvariation)) 
#same from here for all trials


		
			#change(inputfile,'tmp1.inp','PIPES' ,'*', 5, rp+'\t') #vary roughness
			# verity only
			#change('tmp1.inp',outputfile,'EMITTERS' , lp, 1, ec+'\r\n') #change emitter at position lp
# Jon exp6 only next line			
			#change('tmp1.inp','tmp4.inp','JUNCTIONS', demandnodes[0], 2, d5) #vary demands (col 2) exp6 only
# Jon exp3 and exp4 only next 4 lines
# for exp 3,4,5 only			change('tmp1.inp','tmp2.inp','JUNCTIONS', demandnodes[0], 2, d5) #vary demands (col 2)
# for exp 3,4,5 only			change('tmp2.inp','tmp3.inp','JUNCTIONS', demandnodes[1], 2, d9) #vary demands
# for exp 3,4,5 only			change('tmp3.inp','tmp4.inp','JUNCTIONS', demandnodes[2], 2, d11) #vary demands
# for exp 6	change('tmp4.inp',outputfile,'EMITTERS' , lp, 1, ec+'\r\n') #change emitter at position lp

