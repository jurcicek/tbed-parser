#!/usr/bin/env python2.5

from trainer import *
import getopt
import sys

trainData   = 'debug.sem'
trainData   = 'debug500.sem'

trgCond = {'nGrams':2, 'nStarGrams':3, 'tplGrams':1, 'speechAct':1, 'lngth':1, 'hasSlots':1}

tmpData = ''

outBestRulesTXT='results.rules'
outBestRulesPickle='results.pckl-bestrules'
outDecoderPickle='results.pckl-decoder'
outVocabulary='results.pckl-vocabulary'

##############################################################################
def usage():
    print("""
Usage:   tbed-trainer.py [options] 

Description:
    Train Transformation-based Error-driven parser.

Options: 
    -h                    : print this help message and exit
    -v                    : produce verbose output
    -p                    : profile
    --trainData=FILE      : CUED format dialogue acts {%s}
    --tmpData=DIR         : directory for temporal data of the parser {%s}
    --outRules=FILE       : output rules file {%s}
    --outPickle=FILE      : output rules file with rules in Pickle format
                            suitable for Python pograms {%s}
    --outDecoderPickle=FILE: output decoder in Pickle format 
                            suitable for Python pograms {%s}
    --trgCond=STR         : {%s}
        nGrams=NUMBER     : grams type generated for triggers 
                            (1 - unigrams, 2 - bigrams, 3 - trigrams)
        nStarGrams=NUMBER : star grams type generated for triggers 
                            (3 - trigrams e.g. ('was', '*', 'hard'), 
                            4 - four grams ('x','*',*','y') 
        tplGrams=NUMBER   : grams x grams used for triggers 
                            (1 - just trgNGrams, 2 - 2xtrgNGrams)
        speechAct=NUMBER  : 0 - no dependence on speech act
                            1 - some triggers depend on speech acts
        lngth=NUMBER      : 0 - no dependence on length of the input word 
                                sequence
                            1 - some triggers depend on the length of the 
                                input word sequence
        hasSlots=NUMBER   : 0 - no dependence on whether DA has slots or not
                            1 - a rule can depend on whether DA has slots 
                                or not
    --outDict=FILE     : output file speed up dictionary{%s}
    """ % (trainData,
           tmpData, 
           outBestRulesTXT, 
           outBestRulesPickle,
           outDecoderPickle,
           trgCond,
           outVocabulary))
           
##############################################################################

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hvp", 
        ["trainData=",
         "outRules=", 
         "outPickle=",
         "outDecoderPickle=",
         "trgCond=",
         "tmpData=",
         'outDict='])
         
except getopt.GetoptError, exc:
    print("ERROR: " + exc.msg)
    usage()
    sys.exit(2)

verbose = False
profile = False
for o, a in opts:
    if o == "-h":
        usage()
        sys.exit()
    elif o == "-v":
        verbose = True
    elif o == "-p":
        profile = True
    elif o == "-t":
        text = True
    elif o == "--trainData":
        trainData = a
    elif o == "--tmpData":
        tmpData = a
    elif o == "--outRules":
        outBestRulesTXT = a
    elif o == "--outPickle":
        outBestRulesPickle = a
    elif o == "--outDecoderPickle":
        outDecoderPickle = a
    elif o == "--outDict":
        outVocabulary = a
    elif o == "--trgCond":
        trgCond = eval(a)

if verbose:
    print "---------------------------------------------"
    print "TBED trainer"
    print "---------------------------------------------"

trn = Trainer(trgCond = trgCond, tmpData = tmpData)
print trn.trgCond

trn.loadData(trainData)

if profile:
    # sometimes is needed to delete *.pyc files because psyco is used if you do 
    # not proile
    import cProfile
    cProfile.run('trn.train()', tmpData+'/trn.train.profile')
else:
    import psyco
    psyco.full()
    trn.train()

trn.writeDecoderPickle(outDecoderPickle)
trn.writeBestRulesTXT(outBestRulesTXT)
trn.writeBestRulesPickle(outBestRulesPickle)
trn.writeVocabulary(outVocabulary)

if verbose:
    print "---------------------------------------------"
    print "TBED trainer: end"
    print "---------------------------------------------"
