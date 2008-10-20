#!/usr/bin/env python2.5

from math import *

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
        s += 'SubSlot: %s - ' % str(self.subSlot)
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
            if not self.subSlot[0] in da.slots:
                if self.subSlot[0] in da.tbedSlots:
                    # there is slot which migth be benefitial to substitue
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
        
    def apply(self, da):
        # change the speech act
        if self.speechAct:
            da.tbedSpeechAct = self.speechAct
            return
        
        # update slots
        if self.addSlot:
            # I expect that slot items are unique, I can not have two the same 
            # slot items in the semantics 
            da.tbedSlots.add(self.addSlot)
            return
            
        if self.delSlot:
            for slt in da.tbedSlots:
                if slt == self.delSlot:
                    da.tbedSlots.remove(slt)
                    break

        if self.subSlot:
            for slt in da.tbedSlots:
                if slt == self.subSlot[0]:
                    da.tbedSlots.remove(slt)
                    da.tbedSlots.add(self.subSlot[1])
                    break
        
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
        
        if self.speechAct:
            s += 'Transformation:SpeechAct:'+str(self.speechAct)+'\n'
        if self.addSlot:
            s += 'Transformation:AddSlot:'+str(self.addSlot)+'\n'
        if self.delSlot:
            s += 'Transformation:DelSlot:'+str(self.delSlot)+'\n'
        if self.subSlot:
            s += 'Transformation:SubSlot:'+str(self.subSlot)+'\n'
            
        return s
        
