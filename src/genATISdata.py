#!/usr/bin/env python2.5

from collections import *
from utils import *
from slotDatabase import *

import glob,re

atisDB = '/home/filip/cued/ATIS/db_filip'
atisTrainSlotsFN = '/home/filip/cued/ATIS/atis_train.slots'
atisTrainOutFN = '/home/filip/cued/ATIS/atis-train.sem.new'

atisTestNorFN = '/home/filip/cued/ATIS/atis3_test_nov93.nor'
atisTestFrmFN = '/home/filip/cued/ATIS/atis3_test_nov93_can.frm'
atisTestOutFN = '/home/filip/cued/ATIS/atis-test.sem.new'

atisDevNorFN = '/home/filip/cued/ATIS/atis3_test_dec94.nor'
atisDevFrmFN = '/home/filip/cued/ATIS/atis3_test_dec94_can.frm'
atisDevOutFN = '/home/filip/cued/ATIS/atis-dev.sem.new'

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

def genTrainData():
    atisTrainSlots = file(atisTrainSlotsFN)
    atisTrainOut = file(atisTrainOutFN, 'w')

    noSlot = set()
    noSlotOk = set([('ground_service',), ('meaning',), ('airline',), ('flight',), ('code',), ('and',), ('airfare',), ('cost',), ('airfare_code',), ('arrive_time.time_range',), ('depart_time.time_range',), ('arrive_time.period_of_day',), ('depart_time.period_of_day',), ('depart_date.time',),  ('arrive_date.time',), ('then',), ('return',), ('distance',), ('connect',), ('downtown',), ('city',), ('toloc.downtown',), ('fromloc.downtown',), ('aircraft',), ('flight_no',), ('airport',), ('toloc.airport',), ('fromloc.airport',), ('flight_mod',), ('flight_time',), ('mod',), ('flight_stop',), ('propulsion',), ('quantyti',), ('location',) , ('capacity',), ('class_type',) ])

    while(True):
        text = ' '.join(atisTrainSlots.readline().strip().split()[1:-1])
        orig = text
        if not text:
            break
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
                print '='+es

        if p:
            print orig
            print text
            print dat
            print slots
            print newSlots
            print '-'*80
            
        da = dat+'('+','.join(newSlots)+')'
        atisTrainOut.write('%s <=> %s\n' % (orig, da))
    ##    print orig
    ##    print text
    ##    print dat
    ##    print slots
    ##    print newSlots
    ##    print '-'*80
        
    print sorted(noSlot)

    print noSlotOk      

    atisTrainOut.close()

##############################################################################
##############################################################################

def genTestData(atisFrmFN, atisNorFN, atisOutFN):
    atisFrm = file(atisFrmFN)
    atisNor = file(atisNorFN)
    atisOut = file(atisOutFN, 'w')
    
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
        
    atisOut.close()
    
    for e in sorted(dats):
        print e
    
    
##############################################################################
##############################################################################
    
genTrainData()

genTestData(atisTestFrmFN, atisTestNorFN, atisTestOutFN)
genTestData(atisDevFrmFN, atisDevNorFN, atisDevOutFN)
