#!/usr/bin/env python2.5

from trainer import *
import getopt
import sys

trainData   = 'debug500.sem'
db          = 'debug_db'

trgCond = {'nGrams':2, 'nStarGrams':3, 'speechAct':1, 'nSlots':1, 'hasSlots':1}

tmpData = ''
outBestRulesTXT='results.rules'
outBestRulesPickle='results.pckl-bestrules'
outDecoderPickle='results.pckl-decoder'

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
        speechAct=NUMBER  : 0 - no dependence on speech act
                            1 - some triggers depend on speech acts
        nSlots=NUMBER     : 0 - no dependence on slots
                            1 - some triggers may depend on already 
                                added slot
        hasSlots=NUMBER   : 0 - no dependence on whether DA has slots or not
                            1 - a rule can depend on whether DA has slots 
                                or not
    --db=DIR              : directory with TAB files which contains database items 
                            for slot names and values{%s}
    """ % (trainData,
           tmpData, 
           outBestRulesTXT, 
           outBestRulesPickle,
           outDecoderPickle,
           trgCond,
           db))
           
##############################################################################

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hvp", 
        ["trainData=",
         "outRules=", 
         "outPickle=",
         "outDecoderPickle=",
         "trgCond=",
         "tmpData=",
         'outDict=',
         'db='])
         
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
    elif o == "--db":
        db = a

if verbose:
    print "---------------------------------------------"
    print "TBED trainer"
    print "---------------------------------------------"

trn = Trainer(trgCond = trgCond, tmpData = tmpData)
print trn.trgCond

trn.loadDB(db)
trn.loadData(trainData, pruneSingletons = True)

if profile:
    # sometimes is needed to delete *.pyc files because psyco is used if you do 
    # not proile
    import cProfile
    cProfile.run('trn.train()', tmpData+'/trn.train.profile')
else:
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    trn.train()

trn.writeDecoderPickle(outDecoderPickle)
trn.writeBestRulesTXT(outBestRulesTXT)
trn.writeBestRulesPickle(outBestRulesPickle)

if verbose:
    print "---------------------------------------------"
    print "TBED trainer: end"
    print "---------------------------------------------"

