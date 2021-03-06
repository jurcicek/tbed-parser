#!/usr/bin/env python2.5

from math import *

from dialogueAct import *
from transformation import *
from trigger import *
        
class Rule:
    def __init__(self, trigger, transformation):
        self.trigger = trigger
        self.transformation = transformation
        self.occurence = 0
        self.netScore = -1000000
        
        return 
    
    def __str__(self):
        s = 'RULE:'
        s += str(self.trigger) #+'\n'
        s += str(self.transformation) 
        
        return s
        
    def __eq__(self, other):
        if not isinstance(other, Rule):
            return False
            
        if self.trigger == other.trigger and self.transformation == other.transformation:
            return True
        
        return False
        
    def __hash__(self):
        h = hash(self.trigger)
        h += hash(self.transformation)
        
        return h % (1 << 31) 
    
    def getOccurance(self):
        return self.transformation.getOccurance()
        
    # measure whether the difference in accuracy after applying 
    # the rule 
    def measureDiff(self, da):
        if self.trigger.validate(da):
            return self.transformation.measureDiff(da)
        else:
            # no difference in performance because I can not 
            # apply the rule
            return 0
        
    def apply(self, da):
        # apply transformation on the dialogue act
        if self.trigger.validate(da):
            applied = self.transformation.apply(da, self.trigger)
        
            if applied:
                da.ruleTracker.append((self, da.renderTBED(False)))
        return 
    
    def complexity(self):
        return self.trigger.complexity()+self.transformation.complexity()

    def cmpOcc(self, r):
        ''' cmp function for sort() '''
        ret = cmp(self.occurence, r.occurence)
        
        return ret
        
    def cmpPlx(self, r):
        ''' cmp function for sort() '''
        
        if self.netScore == r.netScore == -1000000:
            return 0
            
        ret = cmp(r.netScore,self.netScore)
        
        if ret == 0:
            ret = cmp(self.complexity(),r.complexity())
            
        return ret
    
    def setPerformance(self, netScore):
        self.netScore = netScore
        
    @classmethod
    def read(cls, nRules):
        # constructor for lines
        nTriggers = filter(lambda r: r[1].startswith('Trigger:') != 0, nRules)
        nTrans = filter(lambda r: r[1].startswith('Transformation:') != 0, nRules)
        
        trigger = Trigger.read(nTriggers)
        trans = Transformation.read(nTrans)
        
        return cls(trigger, trans)
        
    def write(self, i):
        s = '-------------------------------------------------------------\n'
        s+= 'Rule:%d:Occ:%d:Net:%d\n' % (i, self.occurence, self.netScore)
        s+= self.trigger.write()
        s+= self.transformation.write()
        
        return s

def getRules(da, trgCond):
    # explode trans & triggers
    # performe cartesion product of triggers and transformations
    
    rules = []
    triggers = da.genTriggers()
    
    if len(triggers) != 0:
        for tran in da.genTrans():
            for trigger in triggers:
                if tran.addSlot != None and trigger.gram == None:
                    # I do not want to add slot which was not 
                    # triggered by some lexical item 
                    continue
                if tran.addSlot != None and tran.addSlot.value.startswith('sv_'):
                    if tran.addSlot.value not in trigger.gram:
                        # I do not want to add slot item with generalized (based not database)
                        # slot value if it was not triggered by found slot value in the input
                        # word sequence
                        continue

                if tran.delSlot != None and trigger.gram == None:
                    # I do not want to del slot with rule which was not 
                    # triggered by some lexical item 
                    continue
                    
                if tran.subSlot != None and trigger.gram == None:
                    # I do not want to sub slot with rule which was not 
                    # triggered by some lexical item 
                    continue
                    
                r = Rule(trigger, tran)
                rules.append(r)
    
    return rules, triggers
