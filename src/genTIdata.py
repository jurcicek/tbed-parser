#!/usr/bin/env python2.5

from collections import *
from utils import *
from slotDatabase import *

import glob,re,os

iiStop = 10000

tiDB = '/home/filip/cued/TownInfoClassic/db_filip'

tiTrainSemFN = '/home/filip/cued/TownInfoClassic/towninfo-train.sem'
tiTrainSemCapsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-train.sem.cap'
tiTrainSemRASPOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-train.sem.rasp'
tiTrainSemDepsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-train.sem.dep'

tiTestSemFN = '/home/filip/cued/TownInfoClassic/towninfo-test.sem'
tiTestSemCapsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-test.sem.cap'
tiTestSemRASPOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-test.sem.rasp'
tiTestSemDepsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-test.sem.dep'

tiDevSemFN = '/home/filip/cued/TownInfoClassic/towninfo-dev.sem'
tiDevSemCapsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-dev.sem.cap'
tiDevSemRASPOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-dev.sem.rasp'
tiDevSemDepsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-dev.sem.dep'

tiTrainAsrFN = '/home/filip/cued/TownInfoClassic/towninfo-train.asr'
tiTrainAsrCapsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-train.asr.cap'
tiTrainAsrRASPOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-train.asr.rasp'
tiTrainAsrDepsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-train.asr.dep'

tiTestAsrFN = '/home/filip/cued/TownInfoClassic/towninfo-test.asr'
tiTestAsrCapsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-test.asr.cap'
tiTestAsrRASPOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-test.asr.rasp'
tiTestAsrDepsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-test.asr.dep'

tiDevAsrFN = '/home/filip/cued/TownInfoClassic/towninfo-dev.asr'
tiDevAsrCapsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-dev.asr.cap'
tiDevAsrRASPOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-dev.asr.rasp'
tiDevAsrDepsOutFN = '/home/filip/cued/TownInfoClassic/new.towninfo-dev.asr.dep'

sdb = SlotDatabase()
sdb.loadTAB(tiDB, False)

##for sn in sdb.slotNamesValues:
##    print sn
##    for each in sdb.slotNamesValues[sn]:
##        print each
##for each in sdb.slotNamesValues['fare_basis_code']:
##    print each

##############################################################################
##############################################################################

def tagReduction(match):
    value = match.group()
##    print value
    try:
        value = value[:3]
    except:
        pass

##    print value
    
    return value

##############################################################################
##############################################################################

def genData(tiInFN, tiCapsOutFN, tiRASPOutFN, tiDepsOutFN):
    tiIn = file(tiInFN)
    tiCapsOut = file(tiCapsOutFN, 'w')
    tiDepsOut = file(tiDepsOutFN, 'w')    
    dats = set()
    
    while(True):
        text = tiIn.readline().strip().split('<=>')[0].strip()
        if not text:
            break
        tiCapsOut.write('%s\n' % prepareForRASP(text, sdb))
        
    tiIn.close()
    tiCapsOut.close()
    
    os.system("rasp.sh -p'-s' < %s > %s" % (tiCapsOutFN, tiRASPOutFN))

    tiRASPOut = file(tiRASPOutFN, 'r')
    
    rasp = tiRASPOut.readlines()
    wordNumber = re.compile(r':\d+_')
    tagNumber = re.compile(r'\d+\|')
    tag = re.compile(r'_([A-Z]+)|')
    
    i = 0
    while i < len(rasp) :
        sentence = rasp[i].strip().split('|)')
        sentence = sentence[0][2:]
        sentence = tagNumber.sub('|', sentence)
        sentence = tag.sub(tagReduction, sentence)
        sentence = sentence.replace('-NP:',':')
        sentence = sentence.replace('| |',' ').lower()
        
        i += 2

##        print sentence
        tiDepsOut.write('%s|||' % sentence)
        
        deps = []
        try:
            while len(rasp[i].strip()) != 0:
                deps.append(rasp[i].strip())
                i += 1
        except:
            pass
        i += 1
        
        deps = ''.join(deps)
        deps = tagNumber.sub('|', deps)
        deps = deps.replace('-NP:',':')
        deps = tag.sub(tagReduction, deps).lower()
##        print deps
        
        tiDepsOut.write('%s ' % deps)
        tiDepsOut.write('\n')
    
    tiDepsOut.close()
    
    for e in sorted(dats):
        print e
    
    
##############################################################################
##############################################################################
    

genData(tiTrainSemFN, tiTrainSemCapsOutFN, tiTrainSemRASPOutFN, tiTrainSemDepsOutFN)
genData(tiTestSemFN, tiTestSemCapsOutFN, tiTestSemRASPOutFN, tiTestSemDepsOutFN)
genData(tiDevSemFN, tiDevSemCapsOutFN, tiDevSemRASPOutFN, tiDevSemDepsOutFN)

genData(tiTrainAsrFN, tiTrainAsrCapsOutFN, tiTrainAsrRASPOutFN, tiTrainAsrDepsOutFN)
genData(tiTestAsrFN, tiTestAsrCapsOutFN, tiTestAsrRASPOutFN, tiTestAsrDepsOutFN)
genData(tiDevAsrFN, tiDevAsrCapsOutFN, tiDevAsrRASPOutFN, tiDevAsrDepsOutFN)
