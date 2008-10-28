#!/usr/bin/env python2.5

from math import *
from copy import *

class Transformation:
    # I implement only one modification at one time
    # If I allowed to performe more modifications than it would be 
    # to complex
    def __init__(self, speechAct = None, addSlot = None, delSlot = None, subSlot = None):
        self.speechAct = speechAct
        self.addSlot = addSlot
        self.delSlot = delSlot
        self.subSlot = subSlot
        
##        print str(self)
        
        return
        
    def __str__(self):
        s  = 'TRANS:'
        s += 'SpeechAct: %s - ' % str(self.speechAct)
        s += 'AddSlot: %s - ' % str(self.addSlot)
        s += 'DelSlot: %s - ' % str(self.delSlot)
        if self.subSlot != None:
            s += 'SubSlot: (%s,%s) -' % (str(self.subSlot[0]), str(self.subSlot[1]))
        else:
            s += 'SubSlot: None -'
        return s

    def __eq__(self, other):
        if self.speechAct == other.speechAct and self.addSlot == other.addSlot and self.delSlot == other.delSlot and self.subSlot == other.subSlot:
            return True
        
        return False
        
    def __hash__(self):
        h  = hash(self.speechAct)
        h += hash(self.addSlot)
        h += hash(self.delSlot)
        h += hash(self.subSlot)
        
        return h % (1 << 31) 
    
    # measure only difference in performance
    #  1 - for corect modification
    #  0 - for no mofification
    # -1 - for wrong modification
    # I expect to perform only one modification at on time
    def measureDiff(self, da):
        if self.speechAct:
            if self.speechAct == da.speechAct:
                if self.speechAct != da.tbedSpeechAct:
                    return 1
                else:
                    return 0
            else:
                if self.speechAct == da.tbedSpeechAct:
                    # this rule is not responsible for changing 
                    # dialogue act type to wrong dialogue act type because 
                    # the dialogue act type is already wrong
                    return 0
                else:
                    return -1
                
        if self.addSlot:
            ## I should fix this estimate because a slot can be added more than 
            ## once, Imight return more than 1,  or return less -1
            if self.addSlot in da.slots:
                if not self.addSlot in da.tbedSlots:
                    return 1
                else:
                    return 0
            else:
                if self.addSlot in da.tbedSlots:
                    # this rule is not responsible for adding wrong slot because 
                    # the slot is already there
                    return 0
                else:
                    return -1
                    
        if self.delSlot:
            ## I can delete more than one slot at once
            ## according to this I have to compute the benefit
            if not self.delSlot in da.slots:
                if self.delSlot in da.tbedSlots:
                    return 1
                else:
                    return 0
            else:
                if not self.delSlot in da.tbedSlots:
                    # this rule is not responsible for deleting correct slot
                    # because the slot was already deleted before (is missing)
                    return 0
                else:
                    return -1

        if self.subSlot:
            ## I can correct or damage more than one slot
            ## I have to correct computation of benefits of the rule
            
            # the trigger was validated globaly on the whole sentence,
            # now I have to validate the trigger localy
            lexIndexes = trigger.getLexIndexes(da)
            # now I should perform substitution only in proximity of 
            # lexIndexes
            
            if not self.subSlot[0] in da.slots:
                if self.subSlot[0] in da.tbedSlots:
                    # there is slot which might be benefitial to substitue
                    if self.subSlot[1] in da.slots:
                        if not self.subSlot[1] in da.tbedSlots:
                            return 1
                        else:
                            return 0
                    else:
                        return -1
                else:
                    return 0
            else:
                if not self.subSlot[0] in da.tbedSlots:
                    # this rule is not responsible for substituting correct slot
                    # because the slot was already missing before
                    return 0
                else:
                    return -1
                
        return 0
        
    def apply(self, da, trigger):
        # change the speech act
        if self.speechAct:
            da.tbedSpeechAct = self.speechAct
            return
        
        # update slots
        if self.addSlot:
            lexIndexes = trigger.getLexIndexes(da)
##            print '>>>', da
##            print '---', trigger
##            print '+++', lexIndexes
            
            # add all triggered slots, I do not care from where they
            # come from, I just track what lexical items trigeered 
            # addition of these slots
            for each in lexIndexes:
                da.tbedSlots.append(deepcopy(self.addSlot))
                da.tbedSlots[-1].lexIndex.add(each[0])
                da.tbedSlots[-1].lexIndex.add(each[1])
                
            da.computeBorders()
            
        if self.delSlot:
            # I do not track deletion of slots
            for slt in da.tbedSlots:
                if self.delSlot.match(slt):
                    da.tbedSlots.remove(slt)

        if self.subSlot:
            # the trigger was validated globaly on the whole sentence,
            # now I have to validate the trigger localy
            lexIndexes = trigger.getLexIndexes(da)
            # now I should perform substitution only in proximity of 
            # lexIndexes
            for slt in da.tbedSlots:
                if self.subSlot[0].match(slt):
                    # I found matching slot but is the lexical 
                    # trigger in proximity of this slot?
                    for lexIndex in lexIndexes:
                        if slt.proximity(lexIndex) == 'left':
                            self.subSlot[1].transform(slt)
                            
                            # store indexes to the lexical realization of 
                            # the substituted (transformed) slot
                            slt.lexIndex.add(lexIndex[0])
                            slt.lexIndex.add(lexIndex[1])
        
        return
        
    def complexity(self):
        if self.speechAct:
            return 1
        if self.addSlot:
            return 1
        if self.delSlot:
            return 1
        if self.subSlot:
            return 1

        return 0
        
    @classmethod
    def read(cls, nTriggers):
        raise ValueError
        return cls()
        
    def write(self):
        s = ''
        
        if self.speechAct != None:
            s += 'Transformation:SpeechAct:'+str(self.speechAct)+'\n'
        if self.addSlot != None:
            s += 'Transformation:AddSlot:'+str(self.addSlot)+'\n'
        if self.delSlot != None:
            s += 'Transformation:DelSlot:'+str(self.delSlot)+'\n'
        if self.subSlot != None:
            s += 'Transformation:SubSlot: (%s,%s)\n ' % (str(self.subSlot[0]),str(self.subSlot[0]))
        return s
        
