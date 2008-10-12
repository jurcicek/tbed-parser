#!/usr/bin/env python2.5

from trainer import *
import getopt
import sys

#import cProfile
import psyco
psyco.full()

trainData   = 'towninfo-train.sem'
trainData   = 'debug.sem'
trainData   = 'debug200.sem'
#trainData   = 'debug500.sem'
#trainData   = 'debug1500.sem'

nGrams = 2
tplGrams = 1
tmpData = ''

outRules='results.rules'
outPickle='results.pickle'

maxProcessedDAs = 28000

filterOutSlots      = range(12,12)
filterOutSpeechActs = ('xxx', 
## 'ask','affirm', 'bye', 'confirm', 'deny', 'hello','inform',
## 'negate','repeat','reqalts','reqmore','request','restart',
## 'select','thankyou',
                       )

##############################################################################
def usage():
    print("""
    Usage:   tbed-trainer.py [options] 
    
    Description:
             Train Transformation-based Error-driven parser.
    
    Options: 
             -h                 : print this help message and exit
             -v                 : produce verbose output
             --trainData=FILE   : CUED format dialogue acts {%s}
             --tmpData=DIR      : directory for temporal data of the parser {%s}
             --outRules=FILE    : output rules file {%s}
             --outPickle=FILE   : output rules file with rules in Pickle format 
                                  suitable for Python pograms {%s}
             --nGrams=NUMBER    : grams type generated for triggers 
                                  (1 - unigrams, 2 - bigrams, 3 - trigrams) {%d}
             --tplGrams=NUMBER  : grams x grams used for triggers 
                                  (1 - just nGrams, 2 - 2xnGrams) {%d}
    """ % (trainData,
           tmpData, 
           outRules, 
           outPickle,
           nGrams,
           tplGrams))
           
##############################################################################

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hv", 
        ["trainData=",
         "outRules=", 
         "outPickle=",
         "nGrams=",
         "tplGrams="         ,
         "tmpData="])
         
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
    elif o == "--tmpData":
        tmpData = a
    elif o == "--outRules":
        outRules = a
    elif o == "--outPickle":
        outPickle = a
    elif o == "--nGrams":
        nGrams = int(a)
    elif o == "--tplGrams":
        tplGrams = int(a)

if verbose:
    print "---------------------------------------------"
    print "TBED trainer"
    print "---------------------------------------------"

trn = Trainer(fos = filterOutSlots, fosa = filterOutSpeechActs, tplGrams = tplGrams, tmpData = tmpData)

trn.loadData(trainData, maxProcessedDAs, nGrams)

#cProfile.run('trn.train()', 'train.profile')
trn.train()

trn.writeRules(outRules)
trn.writePickle(outPickle)

if verbose:
    print "---------------------------------------------"
    print "TBED trainer: end"
    print "---------------------------------------------"
