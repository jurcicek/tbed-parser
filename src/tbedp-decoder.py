#!/usr/bin/env python2.5

import getopt
import sys
from decoder import *

inPickle = 'debug200.pickle'
testData    = 'towninfo-test.sem'

maxProcessedDAs = 28000

trgCond = {'nGrams':3, 'nStarGrams':4, 'tplGrams':1, 'speechAct':1, 'lngth':1}

filterOutSlots      = range(12,12)
filterOutSpeechActs = ('xxx', 
## 'ask','affirm', 'bye', 'confirm', 'deny', 'hello','inform',
## 'negate','repeat','reqalts','reqmore','request','restart',
## 'select','thankyou',
                       )

                ##############################################################################
def usage():
    print("""
    Usage:   tbed-decoder.py [options] 
    
    Description:
             Decode CUED semantics based obn Transformation-based Error-driven
             rules.
    
    Options: 
             -h                 : print this help message and exit
             -v                 : produce verbose output
             --testData=FILE    : tes data - CUED format dialogue acts {%s}
             --inPickle=FILE    : input rules file with rules in Pickle format 
                                  suitable for Python pograms {%s}
             --inDict=FILE      : input speed up dict {%s}
             --outSem=FILE      : decoded CUED format dialogue acts {%s}
    """ % (testData, 
           inPickle,
           inDict,
           outSem))
           
##############################################################################

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hv", 
        ["testData=",
         "inPickle=",
         'inDict=',
         "outSem="])
         
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
    elif o == "--testData":
        testData = a
    elif o == "--inPickle":
        inPickle = a
    elif o == "--inDict":
        inDict = a
    elif o == "--outSem":
        outSem = a

if verbose:
    print "---------------------------------------------"
    print "TBED decoder"
    print "---------------------------------------------"

dcd = Decoder(fos = filterOutSlots, fosa = filterOutSpeechActs, trgCond = trgCond)

dcd.readPickle(inPickle)
dcd.readDict(inDict)
dcd.loadData(testData, maxProcessedDAs)

dcd.decode()
dcd.writeOutput(outSem)
    
if verbose:
    print "---------------------------------------------"
    print "TBED decoder: end"
    print "---------------------------------------------"
