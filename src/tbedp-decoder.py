#!/usr/bin/env python2.5

import getopt
import sys
from decoder import *

inPickle = 'debug200.pckl-decoder'
testData    = 'towninfo-test.sem'
iniTest = False

##############################################################################
def usage():
    print("""
Usage:   tbed-decoder.py [options] 

Description:
    Decoder of CUED semantics based on Transformation-based Error-driven
    rules which are derived fully automatically.

Options: 
    -h                : print this help message and exit
    -v                : produce verbose output
    -i                : initialize decoding with 'testData'.ini file
    --testData=FILE   : tes data - CUED format dialogue acts {%s}
    --inPickle=FILE   : input decoder file from trainer with rules and 
                        other parameters in Pickle format 
                        suitable for Python pograms {%s}
    --inDict=FILE     : input speed up dict {%s}
    --outSem=FILE     : decoded CUED format dialogue acts {%s}
    """ % (testData, 
           inPickle,
           inDict,
           outSem))
           
##############################################################################

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hvi", 
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
    elif o == "-i":
        iniTest = True
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

print inPickle
dcd = Decoder.readDecoderPickle(inPickle)
print dcd.trgCond

dcd.loadData(testData)
if iniTest:
    dcd.loadTbedData(testData+'.ini')
    
dcd.decode()
dcd.writeOutput(outSem)
    
if verbose:
    print "---------------------------------------------"
    print "TBED decoder: end"
    print "---------------------------------------------"
