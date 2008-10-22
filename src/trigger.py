#!/usr/bin/env python2.5

from math import *

class Trigger:
    def __init__(self, speechAct = None, grams = None, slots = None, lngth = None, hasSlots=None):
        self.speechAct = speechAct
        self.grams = grams
        self.slots = slots
        self.lngth = lngth
        self.hasSlots = hasSlots

        return

    def __str__(self):
        s  = 'TRIGGER:'
        s += 'Grams: %s - ' % str(self.grams)
        s += 'SpeechAct: %s - ' % str(self.speechAct)
        s += 'Slots: %s - ' % str(self.slots)
        s += 'Length: %s - ' % str(self.lngth)
        s += 'HasSlots: %s - ' % str(self.hasSlots)
        
        return s
        
    def __eq__(self, other):
        if self.grams == other.grams and self.speechAct == other.speechAct and self.slots == other.slots and self.lngth == other.lngth and self.hasSlots == other.hasSlots:
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
        if self.hasSlots:
            h += hash(self.hasSlots)
        
        return h % (1 << 31)

    def validate(self, da):
        if self.grams:
            for each in self.grams:
                if not each in da.grams:
                    return False

        if self.speechAct:
            if self.speechAct != da.tbedSpeechAct:
                return False

        if self.lngth != None:
            if self.lngth < len(da.words):
                return False
                
        if self.hasSlots != None:
            if self.hasSlots == 1 and len(da.tbedSlots) > 0:
                return False
            if self.hasSlots == 2 and len(da.tbedSlots) == 0:
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
        if self.lngth != None:
            c += 1
        if self.hasSlots != None:
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
        
        if self.lngth != None:
            s += 'Trigger:Length:'+str(self.lngth)+'\n'
            
        if self.hasSlots != None:
            s += 'Trigger:HasSlots:'+str(self.hasSlots)+'\n'
            
        return s
