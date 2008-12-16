#!/usr/bin/env python2.5

import getopt
import sys
from decoder import *

inPickle = 'debug200.pckl-decoder'
testData    = 'towninfo-test.sem'

##############################################################################
def usage():
    print("""
Usage:   tbed-decoder.py [options] 

Description:
    Decoder of CUED semantics based on Transformation-based Error-driven
    rules which are derived fully automatically.

Options: 
    -h                : print this help message and exit
    -v           ########     : produce verbose output
    --testData=FILE   : tes data - CUED format dialogue acts {%s}
    --inPickle=FILE   : input decoder file from trainer with rules and 
                        other parameters in Pickle format 
                        suitable for Python pograms {%s}
    --inDict=FILE     : input speed up dict {%s}
    --outSem=FILE     : decoded CUED format dialogue acts {%s}
    --db=DIR          : directory with TAB files which contains database items 
                        for slot names and values{%s}
    """ % (testData, 
           inPickle,
           inDict,
           outSem,
           db))
           
##############################################################################

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hv", 
        ["testData=",
         "inPickle=",
         'inDict=',
         "outSem=",
         "db="])
         
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
    elif o == "--db":
        db = a

if verbose:
    print "---------------------------------------------"
    print "TBED decoder"
    print "---------------------------------------------"

print inPickle
dcd = Decoder.readDecoderPickle(inPickle)
print dcd.trgCond

dcd.loadDB(db)
dcd.loadData(testData)
    
dcd.decode()
dcd.writeOutput(outSem)
dcd.writeAlignment(outSem+'.algn')
dcd.writeAnalyze(outSem+'.anlz')
    
if verbose:
    print "---------------------------------------------"
    print "TBED decoder: end"
    print "---------------------------------------------"
