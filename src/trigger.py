#!/usr/bin/env python2.5

from math import *

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
