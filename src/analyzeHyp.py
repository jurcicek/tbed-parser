#!/usr/bin/env python2.5

import getopt
import sys
from decoder import *

inPickle = 'debug200.pickle'
refData    = 'data/towninfo-dev.sem'
hypData    = 'results/test/rules.dev.sem.hyp'

##############################################################################
def usage():
    print("""
Usage:   analyzeHyp.py [options] 

Description:
    The script loads CUED development semantics and compares it with the 
    output of the TBED parser.
    
Options: 
    -h                 : print this help message and exit
    -v                 : produce verbose output
    --refData=FILE     : reference data {%s}
    --hypData=FILE     : hypothesis data {%s}
    """ % (refData, 
           hypData))
           
##############################################################################

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hv", 
        ["refData=",
         "hypData="])
         
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
    elif o == "--refData":
        refData = a
    elif o == "--hypData":
        hypData = a

dcd = Decoder()

dcd.loadData(refData)
dcd.loadTbedData(hypData)

dcd.analyze()

