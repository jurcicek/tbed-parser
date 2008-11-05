#!/usr/bin/env python2.5

import getopt
import sys
from decoder import *

trainData  = '../data/towninfo-train.sem'
devData    = '../data/towninfo-dev.sem'
testData   = '../data/towninfo-test.sem'
trainDataASR  = '../data/towninfo-train.asr'
devDataASR    = '../data/towninfo-dev.asr'
testDataASR   = '../data/towninfo-test.asr'

##############################################################################
def usage():
    print("""
Usage:   orangeTab.py [options] 

Description:
    
Options: 
    -h                 : print this help message and exit
    -v                 : produce verbose output
    --trainData=FILE   : train data {%s}
    --devData=FILE     : dev data {%s}
    """ % (trainData, 
           devData))
           
##############################################################################

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hv", 
        ["trainData=",
         "devData="])
         
except getopt.GetoptError, exc:
    print("ERROR: " + exc.msg)
    usage()
    sys.exit(2)

verbose = False
for o, a in opts:
    if o == "-h":
        usage()
        sys.exit()
    elif o == "-v":
        verbose = True
    elif o == "-t":
        text = True
    elif o == "--trainData":
        trainData = a
    elif o == "--devData":
        devData = a

trgCond = {}
 
trgCond['nGrams'] = 1
#trgCond['nGrams'] = 2
trgCond['nStarGrams'] = 1
trgCond['nStarGrams'] = 3

dcd = Decoder(trgCond)

dcd.loadData(trainData)
dcd.writeOrangeTab(trainData+'.o.txt')

dcd.loadData(devData)
dcd.writeOrangeTab(devData+'.o.txt')

dcd.loadData(testData)
dcd.writeOrangeTab(testData+'.o.txt')

##################################################################333

dcd.loadData(trainDataASR)
dcd.writeOrangeTab(trainDataASR+'.o.txt')

dcd.loadData(devDataASR)
dcd.writeOrangeTab(devDataASR+'.o.txt')

dcd.loadData(testDataASR)
dcd.writeOrangeTab(testDataASR+'.o.txt')
