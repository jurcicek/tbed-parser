#!/usr/bin/env python2.5

from math import *

class Transformation:
    # I implement only one modification at one time
    # If I allowed to performe more modifications than it would be 
    # to complex
    def __init__(self, speechAct = None, addSlot = None, delSlot = None):
        self.speechAct = speechAct
        self.addSlot = addSlot
        self.delSlot = delSlot
        
##        print str(self)
        
        return
        
    def __str__(self):
        s  = 'TRANS:'
        s += 'SpeechAct: %s - ' % str(self.speechAct)
        s += 'AddSlot: %s - ' % str(self.addSlot)
        s += 'DelSlot: %s - ' % str(self.delSlot)
        return s

    def __eq__(self, other):
        if self.speechAct == other.speechAct and self.addSlot == other.addSlot and self.delSlot == other.delSlot:
            return True
        
        return False
        
    def __hash__(self):
        h  = hash(self.speechAct)
        h += hash(self.addSlot)
        h += hash(self.delSlot)
        
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
                return -1
                
        if self.addSlot:
            if self.addSlot in da.slots:
                if not self.addSlot in da.tbedSlots:
                    return 1
                else:
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
                return -1
        
        return 0
        
    def apply(self, da):
        # change the speech act
        if self.speechAct:
            da.tbedSpeechAct = self.speechAct
            return
        
        # update slots
        if self.addSlot:
            da.tbedSlots.add(self.addSlot)
            return
            
        if self.delSlot:
            for slt in da.tbedSlots:
                if slt == self.delSlot:
                    da.tbedSlots.remove(slt)
                    break
        return
        
    def complexity(self):
        if self.speechAct:
            return 1
        if self.addSlot:
            return 1
        if self.delSlot:
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
            
        return s
        
class Trigger:
    def __init__(self, speechAct = None, grams = None, slots = None, lngth = None):
        self.speechAct = speechAct
        self.grams = grams
        self.slots = slots
        self.lngth = lngth

        return

    def __str__(self):
        s  = 'TRIGGER:'
        s += 'Grams: %s - ' % str(self.grams)
        s += 'SpeechAct: %s - ' % str(self.speechAct)
        s += 'Slots: %s - ' % str(self.slots)
        s += 'Length: %s - ' % str(self.lngth)
        
        return s
        
    def __eq__(self, other):
        if self.grams == other.grams and self.speechAct == other.speechAct and self.slots == other.slots and self.lngth == other.lngth:
            return True
        
        return False
        
    def __hash__(self):
        h = 0

        if self.grams:
            for each in self.grams:
                h += hash(each)

        if self.speechAct:
            h += hash(self.speechAct)
        
        if self.slots:
            for each in self.slots:
                h += hash(each)
                
        if self.lngth:
            h += hash(self.lngth)
        
        return h % (1 << 31)

    def validate(self, da):
        if self.grams:
            for each in self.grams:
                if not each in da.grams:
                    return False

        if self.speechAct:
            if self.speechAct != da.tbedSpeechAct:
                return False

        if self.lngth:
            if self.lngth < len(da.words):
                return False
                    
        if self.slots:
            for each in self.slots:
                if not each in da.tbedSlots:
                    return False
    
        return True

    def complexity(self):
        c = 0
        
        if self.grams:
            for each in self.grams:
                c += len(each)
                
        if self.speechAct:
            c += 1

        if self.lngth:
            c += 1
            
        if self.slots:
            c += len(self.slots)

        return c
        
    @classmethod
    def read(cls, nTrans):
        raise ValueError
        return cls()
        
    def write(self):
        s = ''
        if self.grams:
            for each in self.grams:
                s += 'Trigger:Gram:'+str(each)+'\n'

        if self.speechAct:
            s += 'Trigger:SpeechAct:'+str(self.speechAct)+'\n'
        
        if self.slots:
            for each in self.slots:
                s += 'Trigger:Slot:'+str(each)+'\n'
        
        if self.lngth:
            s += 'Trigger:Length:'+str(self.lngth)+'\n'
            
        return s
