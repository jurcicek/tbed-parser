#!/usr/bin/env python2.5

from math import *

class Transformation:
    def __init__(self, speechAct = None, addSlot = None, delSlot = None):
        self.speechAct = speechAct
        self.addSlot = addSlot
        self.delSlot = delSlot
        
##        print str(self)
        
        return
        
    def __str__(self):
        s  = 'TRANS:'
        s += 'SpeechAct: %s - ' % self.speechAct
        s += 'AddSlot: %s - ' % self.addSlot
        s += 'DelSlot: %s - ' % self.delSlot
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
        
    def apply(self, da, tmp):
        # change the speech act
        if self.speechAct:
            if tmp:
                da.tmpTbedSpeechAct = self.speechAct
            else:
                da.tbedSpeechAct = self.speechAct
        
        # update slots
        if self.addSlot:
            if tmp:
                da.tmpTbedSlots.append(self.addSlot)
            else:
                da.tbedSlots.append(self.addSlot)
            
        if tmp:
            if self.delSlot:
                for i in range(len(da.tbedSlots)):
                    if da.tmpTbedSlots[i] == self.delSlot:
                        del da.tmpTbedSlots[i]
                        break
        else:
            if self.delSlot:
                for i in range(len(da.tbedSlots)):
                    if da.tbedSlots[i] == self.delSlot:
                        del da.tbedSlots[i]
                        break
                        
    def complexity(self):
        c = 0
        
        if self.speechAct:
            c += 1
        if self.addSlot:
            c += 1
        if self.delSlot:
            c += 1

        return c
        
    @classmethod
    def read(cls, nTriggers):
        raise ValueError
        return cls()
        
    def write(self):
        s = ''
        
        if self.speechAct:
            s += 'Transformation:SpeechAct:'+self.speechAct+'\n'
        if self.addSlot:
            s += 'Transformation:AddSlot:'+self.addSlot+'\n'
        if self.delSlot:
            s += 'Transformation:DelSlot:'+self.delSlot+'\n'
            
        return s
        
class Trigger:
    def __init__(self, speechAct = None, grams = None, slots = None):
        self.speechAct = speechAct
        self.grams = grams
        self.slots = slots

##        print str(self)
        
        return

    def __str__(self):
        s  = 'TRIGGER:'
        s += 'Grams: %s - ' % str(self.grams)
        s += 'SpeechAct: %s - ' % self.speechAct
        s += 'Slots: %s - ' % str(self.slots)
        
        return s
        
    def __eq__(self, other):
        if self.grams == other.grams and self.speechAct == other.speechAct and self.slots == other.slots:
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
        
        return h % (1 << 31)

    def validate(self, da, tmp):
        if self.grams:
            for each in self.grams:
                if not each in da.grams:
                    return False

        if self.speechAct:
            if tmp:
                if self.speechAct != da.tmpTbedSpeechAct:
                    return False
            else:
                if self.speechAct != da.tbedSpeechAct:
                    return False
        
        if tmp:
            if self.slots:
                for each in self.slots:
                    if not each in da.tmpTbedSlots:
                        return False
        else:
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
                s += 'Trigger:SpeechAct:'+self.speechAct+'\n'
        
        if self.slots:
            for each in self.slots:
                s += 'Trigger:Slot:'+str(each)+'\n'
        
        return s
