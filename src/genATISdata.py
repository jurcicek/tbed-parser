#!/usr/bin/env python2.5

from collections import *
from utils import *
from slotDatabase import *

import glob,re,os

iiStop = 10000

atisDB = '/home/filip/cued/ATIS/db_filip'
atisTrainSlotsFN = '/home/filip/cued/ATIS/atis_train.slots'
atisTrainOutFN = '/home/filip/cued/ATIS/new.atis-train.sem'
atisTrainCapsOutFN = '/home/filip/cued/ATIS/new.atis-train.sem.cap'
atisTrainRASPOutFN = '/home/filip/cued/ATIS/new.atis-train.sem.rasp'
atisTrainDepsOutFN = '/home/filip/cued/ATIS/new.atis-train.sem.dep'

atisTestNorFN = '/home/filip/cued/ATIS/atis3_test_nov93.nor'
atisTestFrmFN = '/home/filip/cued/ATIS/atis3_test_nov93_can.frm'
atisTestOutFN = '/home/filip/cued/ATIS/new.atis-test.sem'
atisTestCapsOutFN = '/home/filip/cued/ATIS/new.atis-test.sem.cap'
atisTestRASPOutFN = '/home/filip/cued/ATIS/new.atis-test.sem.rasp'
atisTestDepsOutFN = '/home/filip/cued/ATIS/new.atis-test.sem.dep'

atisDevNorFN = '/home/filip/cued/ATIS/atis3_test_dec94.nor'
atisDevFrmFN = '/home/filip/cued/ATIS/atis3_test_dec94_can.frm'
atisDevOutFN = '/home/filip/cued/ATIS/new.atis-dev.sem'
atisDevCapsOutFN = '/home/filip/cued/ATIS/new.atis-dev.sem.cap'
atisDevRASPOutFN = '/home/filip/cued/ATIS/new.atis-dev.sem.rasp'
atisDevDepsOutFN = '/home/filip/cued/ATIS/new.atis-dev.sem.dep'

sdb = SlotDatabase()
sdb.loadTAB(atisDB, False)

##for sn in sdb.slotNamesValues:
##    print sn
##    for each in sdb.slotNamesValues[sn]:
##        print each
##for each in sdb.slotNamesValues['fare_basis_code']:
##    print each

##############################################################################
##############################################################################

def replaceSV(text, sn, sv, i):
    return text[0:i]+sn+text[i+len(sv):]
    
def prepareForRASP(text, db):
    valueDictCounter = defaultdict(int)
    valueDict = {}
    p = False
    
    for (sn, sv, svs, c, cc) in db.values:
        while True:
            i = text.find(svs)
            if i != -1:
                # test wheather there are spaces around the word. that it is not a 
                # substring of another word!
                if i > 0 and text[i-1] != ' ':
                    break
                if i < len(text)-len(svs) and text[i+len(svs)] != ' ':
                    break
                        
                # I found the slot value synonym from database in the 
                # sentence, I must replace it
                newSV1 = 'sv_'+sn
                valueDictCounter[newSV1] += 1
                newSV2 = newSV1+'-'+str(valueDictCounter[newSV1])
                valueDict[newSV2] = (sv, svs)
                
                text = replaceSV(text, newSV2, svs, i)

            else:
                break

    words = text.split()
    
    for i, w in enumerate(words):
        if w.startswith('sv_'):
            w = w.lower()
            
            if w.find('_name') != -1 or w.find('manufacturer') != -1:
                words[i] = '-'.join(valueDict[w][1].title().split())
            elif w.find('_code') != -1:
                words[i] = '-'.join(valueDict[w][1].upper().split())
            else:
                words[i] = valueDict[w][1]
                
    words[0] = words[0][0].upper()+words[0][1:]
    
    text = ' '.join(words)+' .'
    
    return text

def tagReduction(match):
    value = match.group()
    try:
        value = value[:2]
    except:
        pass

    return value

def genTrainData():
    atisTrainSlots = file(atisTrainSlotsFN)
    atisTrainOut = file(atisTrainOutFN, 'w')
    atisTrainCapsOut = file(atisTrainCapsOutFN, 'w')
    atisTrainDepsOut = file(atisTrainDepsOutFN, 'w')

    noSlot = set()
    noSlotOk = set([('ground_service',), ('meaning',), ('airline',), ('flight',), ('code',), ('and',), ('airfare',), ('cost',), ('airfare_code',), ('arrive_time.time_range',), ('depart_time.time_range',), ('arrive_time.period_of_day',), ('depart_time.period_of_day',), ('depart_date.time',),  ('arrive_date.time',), ('then',), ('return',), ('distance',), ('connect',), ('downtown',), ('city',), ('toloc.downtown',), ('fromloc.downtown',), ('aircraft',), ('flight_no',), ('airport',), ('toloc.airport',), ('fromloc.airport',), ('flight_mod',), ('flight_time',), ('mod',), ('flight_stop',), ('propulsion',), ('quantyti',), ('location',) , ('capacity',), ('class_type',) ])

    ii = 0
    while(True):
        text = ' '.join(atisTrainSlots.readline().strip().split()[1:-1])
        orig = text
        if not text:
            break
            
        if ii>iiStop:
            break
        ii += 1
        
        dat = atisTrainSlots.readline().lower().strip().split()[1]
        slots = [x for x in atisTrainSlots.readline().lower().strip().split() if x !=dat]
        star = atisTrainSlots.readline().strip()
        
        newSlots = []
        n = 0
        
        p = False
        for es in slots:
    ##        if (es,) in noSlotOk:
    ##            # skip the slot
    ##            continue

            match = False
            for snd in sdb.slotNamesValues:
                if es.endswith(snd):
                    # we found the slot in the database
                    svsMatch = False
                    candidates = []
                    
                    for (sv, svs, c, cc) in sdb.slotNamesValues[snd]:
                        i = 0 
                        while True:
                            i = text.find(svs, i)
                            if i != -1:
                                # test wheather there are spaces around the word. 
                                # that it is not a 
                                # substring of another word!
                                
    ##                            if es == 'or':
    ##                                print '#',svs,text[i-1:]
                                    
                                if i > 0 and text[i-1] != ' ':
                                    i += 1
                                    continue
                                if i < len(text)-len(svs) and text[i+len(svs)] != ' ':
                                    i += 1
                                    continue
                                        
    ##                            if es == 'or':
    ##                                print '#passed'
                                
                                candidates.append((i, svs, sv, svs.count(' '), len(svs)))
                                
                                svsMatch = True
                                
                            break

                    if svsMatch:
                        candidates.sort(cmp=lambda x,y: cmp(x[0], y[0]) if x[0] != y[0] else cmp(y[3], x[3]) if x[3] != y[3] else cmp(y[4], x[4]))
    ##                    print candidates
                        
                        text = text[0:candidates[0][0]]+'*'+str(n)+'*'+text[candidates[0][0]+len(candidates[0][1]):]
                        n += 1
                        newSlots.append(es+'="'+candidates[0][2]+'"')
                    else:
    ##                    newSlots.append(es+'="found slot name, not value"')
                        newSlots.append(es+'="value"')
                        p = True
                        print '-'+es
                    
                    match = True
                    break
                    
            if not match:
    ##            newSlots.append(es+'="no slot name"')
                newSlots.append(es+'="value"')
                noSlot.add(es)
                
                p = True
##                print '='+es

##        if p:
##            print orig
##            print text
##            print dat
##            print slots
##            print newSlots
##            print '-'*80
            
        da = dat+'('+','.join(newSlots)+')'
        atisTrainOut.write('%s <=> %s\n' % (orig, da))
        
##        print '%s <=> %s' % (orig, da)
        
        
        atisTrainCapsOut.write('%s\n' % prepareForRASP(orig, sdb))
        
    ##    print orig
    ##    print text
    ##    print dat
    ##    print slots
    ##    print newSlots
    ##    print '-'*80
        
##    print sorted(noSlot)
##    print noSlotOk      

    atisTrainOut.close()
    atisTrainCapsOut.close()

    os.system("rasp.sh -p'-s' < %s > %s" % (atisTrainCapsOutFN, atisTrainRASPOutFN))

    atisTrainRASPOut = file(atisTrainRASPOutFN, 'r')
    
    rasp = atisTrainRASPOut.readlines()
    wordNumber = re.compile(r':\d+_')
    tagNumber = re.compile(r'\d+\|')
    tag = re.compile(r'([A-Z]+)|')
    
    i = 0
    while i < len(rasp) :
        sentence = rasp[i].strip().split('|)')
        sentence = sentence[0][2:]
##        sentence = wordNumber.sub(':', sentence)
        sentence = tagNumber.sub('|', sentence)
        sentence = tag.sub(tagReduction, sentence)
        sentence = sentence.replace('| |',' ').lower()
##        sentence = sentence.replace(':_',':')
        
        i += 2

##        print sentence
        atisTrainDepsOut.write('%s|||' % sentence)
        
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
        deps = tag.sub(tagReduction, deps).lower()
##        print deps
        
        atisTrainDepsOut.write('%s ' % deps)
        atisTrainDepsOut.write('\n')
    
    atisTrainDepsOut.close()
    
##############################################################################
##############################################################################

def genTestData(atisFrmFN, atisNorFN, atisOutFN, atisCapsOutFN, atisRASPOutFN, atisDepsOutFN):
    atisFrm = file(atisFrmFN)
    atisNor = file(atisNorFN)
    atisOut = file(atisOutFN, 'w')
    atisCapsOut = file(atisCapsOutFN, 'w')
    atisDepsOut = file(atisDepsOutFN, 'w')    
    dats = set()
    
    while(True):
        text = ' '.join(atisNor.readline().strip().split()[1:-1])
        orig = text
        if not text:
            break
        unormText = ' '.join(atisFrm.readline().strip().split()[1:-1])
        dat = atisFrm.readline().lower().strip().split()[1]
        
        if dat == 'aircarft':
            dat = 'aircraft'
    
        dats.add(dat)
        
        slots = []
        while True:
            star = atisFrm.readline().strip()
            if star == '*':
                break
            
            # star is not a star
            slot = [x.strip() for x in star.lower().split('=')]
            slotName = slot[0]
            slotValue = slot[1]
            
            if slotName == 'depart_time.period_of_day' and slotValue == '12pm':
                slotValue = 'noon'
                
            if slotName == 'depart_time.time' and slotValue == '12pm':
                i = orig.find('noon')
                ii = unormText.find('12pm')
                
                if i != -1 and ii!=-1:
                    slotName = 'depart_time.period_of_day'
                    slotValue = 'noon'
                    
                
            # I have unify the slot value
            for snd in sdb.slotNamesValues:
                if slotName.endswith(snd):
                    # we found the slot in the database
                    candidates = []
                    
                    for (sv, svs, c, cc) in sdb.slotNamesValues[snd]:
                        if slotValue == svs:
                            slotValue = sv
                            break
                    else:
                        print orig
                        print unormText
                        print 'slotName: %s slotValue %s not in database.' % (slotName, slotValue)

            slot = str(slotName)+'="'+str(slotValue)+'"'
            slots.append(slot)
            
        atisOut.write(orig +' <=> '+dat+'('+','.join(slots)+')\n')
        atisCapsOut.write('%s\n' % prepareForRASP(orig, sdb))
        
    atisOut.close()
    atisCapsOut.close()
    
    os.system("rasp.sh -p'-s' < %s > %s" % (atisCapsOutFN, atisRASPOutFN))

    atisRASPOut = file(atisRASPOutFN, 'r')
    
    rasp = atisRASPOut.readlines()
    wordNumber = re.compile(r':\d+_')
    tagNumber = re.compile(r'\d+\|')
    tag = re.compile(r'([A-Z]+)|')
    
    i = 0
    while i < len(rasp) :
        sentence = rasp[i].strip().split('|)')
        sentence = sentence[0][2:]
##        sentence = wordNumber.sub(':', sentence)
        sentence = tagNumber.sub('|', sentence)
        sentence = tag.sub(tagReduction, sentence)
        sentence = sentence.replace('| |',' ').lower()
##        sentence = sentence.replace(':_',':')
        
        i += 2

##        print sentence
        atisDepsOut.write('%s|||' % sentence)
        
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
        deps = tag.sub(tagReduction, deps).lower()
##        print deps
        
        atisDepsOut.write('%s ' % deps)
        atisDepsOut.write('\n')
    
    atisDepsOut.close()
    
    for e in sorted(dats):
        print e
    
    
##############################################################################
##############################################################################
    
genTrainData()

genTestData(atisTestFrmFN, atisTestNorFN, atisTestOutFN, atisTestCapsOutFN, atisTestRASPOutFN, atisTestDepsOutFN)
genTestData(atisDevFrmFN, atisDevNorFN, atisDevOutFN, atisDevCapsOutFN, atisDevRASPOutFN, atisDevDepsOutFN)
