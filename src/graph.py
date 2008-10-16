#!/usr/bin/env python2.5

import sys, struct, commands, getopt, sys, os.path
from pylab import *

from decoder import *

binDir = '../../bin'
resultsDir=''

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hp", 
        ["resultsDir=",
         'dataDir='])
         
except getopt.GetoptError, exc:
    print("ERROR: " + exc.msg)
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-h":
        usage()
        sys.exit()
    elif o == "--resultsDir":
        resultsDir = a
    elif o == "--dataDir":
        dataDir = a

def decode(data, inPickle, inDict, nRules = 0):
    outSem = 'graph.sem'
    maxProcessedDAs = 28000
    trgCond = {'nGrams':3, 'nStarGrams':4, 'tplGrams':1, 'speechAct':1, 'lngth':1}
    filterOutSlots      = range(12,12)
    filterOutSpeechActs = ('xxx',)
    
    dcd = Decoder(fos = filterOutSlots, fosa = filterOutSpeechActs, trgCond = trgCond)

    maxRules = dcd.readPickle(inPickle, nRules)
    dcd.readDict(inDict)
    dcd.loadData(data, maxProcessedDAs)
    dcd.decode()
    dcd.writeOutput(outSem)

    o = commands.getoutput('%s/cuedSemScore.pl -d %s %s' % (binDir, outSem, data))
    o = o.split()
    
    return maxRules, o[0], o[3]

    
def decodeSet(data):
    data = os.path.join(dataDir, data)
    inPickle = os.path.join(resultsDir, 'rules.pickle')
    inDict = os.path.join(resultsDir, 'rules.pckl-dict')
    
    i = 16
    iMax = 30

    nRules = []
    acc = []
    fm = []
    
    print data
    while i<iMax:
        iMax, a, f = decode(data, inPickle, inDict, i)
        acc.append(float(a))
        fm.append(float(f))
        nRules.append(i)
        print i, iMax, a, f
        
        if i+1 == iMax:
            break
            
        i += int(iMax/2)
        
        if i > iMax:
            i = iMax-1
            
    return acc, fm, nRules
    

def findMax(data):
    max = 0
    iMax = 0
    
    for i in range(len(data)):
        if data[i]> max:
            iMax = i
            max = data[i]
    
    return iMax
    
outGraph = os.path.join(resultsDir,'rules.performance.clean.eps')
settingsFN = os.path.join(resultsDir,'settings')
trainCleanAcc, trainCleanF, nRules = decodeSet('towninfo-train.sem')
devCleanAcc, devCleanF, nRules = decodeSet('towninfo-dev.sem')
testCleanAcc, testCleanF, nRules = decodeSet('towninfo-test.sem')

f = file(settingsFN, 'r')
for s in f.readlines():
    if s.startswith('TBEDP_TRN_DATA_FILE'):
        settings = s.replace('TBEDP_TRN_DATA_FILE=', '')
f.close()

fig = figure(figsize=(11.7, 8.3))

title('Clean data - training data: '+settings)

xlabel('nRules - number of used rules')
ylabel('Acc [%], F[%]')

plot(nRules, trainCleanAcc, "g-.")
plot(nRules, trainCleanF,  "g-")

plot(nRules, devCleanAcc, "b-.")
plot(nRules, devCleanF,  "b-")

plot(nRules, testCleanAcc, "r-.")
plot(nRules, testCleanF,  "r-")

legend(("train data - clean - Accurracy",
        "train data - clean - Item F-masure", 
        "  dev data - clean - Accurracy",
        "  dev data - clean - Item F-masure",         
        " test data - clean - Accurracy",
        " test data - clean - Item F-masure"),         
        loc = "lower right")

grid(True)

i = findMax(devCleanF)
plot([nRules[i]], [devCleanF[i]], 'bs-')

annotate('Best performance on dev set.', (nRules[i], devCleanF[i]), 
        (nRules[i]-25, devCleanF[i]-7), 
        arrowprops=dict(facecolor='black', shrink=0.05, width=1),
        fontsize=14)

xlim(xmin=nRules[0]-2)

text(nRules[i]-25, devCleanF[i]-9, 'Test data: \n- Acc=%.2f \n- F=%.2f' % (testCleanAcc[i], testCleanF[i]), fontsize=14)

savefig(outGraph)

print commands.getoutput("epstopdf %s" % (outGraph))
print commands.getoutput("rm -f %s" % (outGraph))


outGraph = os.path.join(resultsDir,'rules.performance.asr.eps')
trainCleanAcc, trainCleanF, nRules = decodeSet('towninfo-train.asr')
devCleanAcc, devCleanF, nRules = decodeSet('towninfo-dev.asr')
testCleanAcc, testCleanF, nRules = decodeSet('towninfo-test.asr')

fig = figure(figsize=(11.7, 8.3))
title('ASR data - training data: '+settings)
xlabel('nRules - number of used rules')
ylabel('Acc [%], F[%]')

plot(nRules, trainCleanAcc, "g-.")
plot(nRules, trainCleanF,  "g-")

plot(nRules, devCleanAcc, "b-.")
plot(nRules, devCleanF,  "b-")

plot(nRules, testCleanAcc, "r-.")
plot(nRules, testCleanF,  "r-")

legend(("train data - ASR - Accurracy",
        "train data - ASR - Item F-masure", 
        "  dev data - ASR - Accurracy",
        "  dev data - ASR - Item F-masure",         
        " test data - ASR - Accurracy",
        " test data - ASR - Item F-masure"),         
        loc = "lower right")

grid(True)

i = findMax(devCleanF)
plot([nRules[i]], [devCleanF[i]], 'bs-')

annotate('Best performance \non dev set.', (nRules[i], devCleanF[i]), 
        (nRules[i]-25, devCleanF[i]-7), 
        arrowprops=dict(facecolor='black', shrink=0.05, width=1),
        fontsize=14)

xlim(xmin=nRules[0]-2)

text(nRules[i]-25, devCleanF[i]-9, 'Test: Acc=%.2f F=%.2f' % (testCleanAcc[i], testCleanF[i]), fontsize=14)

savefig(outGraph)
print commands.getoutput("epstopdf %s" % (outGraph))
print commands.getoutput("rm -f %s" % (outGraph))
