#!/usr/bin/env python2.5

from string import *
import re
import os.path
from threading import *

from copy import *

from utils import *
from slot import *
from dialogueAct import *
from rule import *

from baseTD import *

class Trainer(BaseTD):
    def __init__(self, fos, fosa, tplGrams ,tmpData):
        BaseTD.__init__(self, fos = fos, fosa = fosa)
        self.tplGrams = tplGrams
        self.tmpData = tmpData
        return

    def findBestRule(self):
        self.rules = {}
        # get all applicable rules
        for da in self.das:
            rs = getRules(da, self.tplGrams)
            
            for r in rs:
                self.rules[r] = self.rules.get(r,0) + 1

        for r in self.rules:
            r.occurence = self.rules[r]
            
##        print rules.values()
        print '---------------------------------------------------------'
        print 'Number of applicable rules %d: ' % len(self.rules)
        print '---------------------------------------------------------'
        
        self.rls = self.rules.keys()

        # apply each rule and measure the score
        for rule in self.rls:
            Ha = Na = Hi = Ri = Ni = 0
            for da in self.das:
                afterRuleDA = copy(da)
                rule.apply(afterRuleDA)
                
                pHa, pNa, pHi, pRi, pNi = afterRuleDA.measure()
                
                Ha += pHa
                Na += pNa
                Hi += pHi
                Ri += pRi
                Ni += pNi
            
            try:
                acc  = 100.0*Ha/Na
            except ZeroDivisionError:
                acc  = 0.0

            try:
                prec = 100.0*Hi/Ri
                rec  = 100.0*Hi/Ni
                f = 2*prec*rec/(prec+rec)
                af = 2*acc*f/(acc+f)
            except ZeroDivisionError:
                prec = 0.0
                rec  = 0.0
                f    = 0.0
                af   = 0.0
                
            rule.setPerformance(af, acc, f, prec, rec)
            
##            print rule, af, acc, f
        
        # sort rules accordin their performance and complexity
        
        self.rls.sort(cmp=lambda x,y: x.cmpPlx(y))
            
        if len(self.rls) == 0:
            print 'No applicable rules.'
            return None, 0.0
        else:
            print 'Best: %s AF:%.2f Cplx:%d Occ:%d' % (self.rls[0], self.rls[0].af, self.rls[0].complexity(), self.rules[self.rls[0]])
            for i in range(1,10):
                print ' Opt: %s AF:%.2f Cplx:%d Occ:%d' % (self.rls[i], self.rls[i].af, self.rls[i].complexity(), self.rls[i].occurence)
        
        return self.selectBestRules(self.rls[:10])

    def applyBestRule(self, bestRule):
        for da in self.das:
            bestRule.apply(da)
    
    def selectBestRules(self, bestRules):
        br = []
        br.append(bestRules[0])

        if br[0].prec - br[0].rec > 2.0:
            # there is too much higher precision than recall
            # I have to encourage increase perferomance in recall because
            # this learning is very defensive = 
            # it slowly increases the recall
            for i in range(1, len(bestRules)):
                if bestRules[i].transformation.addSlot == None:
                    continue
                elif bestRules[i].transformation.speechAct != None:
                    continue
                elif bestRules[i].transformation.delSlot != None:
                    continue
                elif bestRules[i].af < self.prevAF:
                    continue
                elif bestRules[i].transformation.addSlot == bestRules[i-1].transformation.addSlot:
                    # remove duplicates
                    continue
                    
                br.append(bestRules[i])

##        for r in br:
##            print '<<<Slct: %s AF:%.2f Cplx:%d' % (r, r.af, r.complexity())
        
        br.reverse()
        sr = []
        # filter out the same (duplict) opperations
        for i in range(0, len(br)):
            ok = True
            for j in range(i+1, len(br)):
                if br[i].transformation.addSlot == br[j].transformation.addSlot:
                    # remove duplicates
                    ok = False
                    break
                
            if ok:
                sr.append(br[i])
        
        sr.reverse()
        
        for r in sr:
            print 'Slct: %s AF:%.2f Cplx:%d' % (r, r.af, r.complexity())
                
        return sr
    
    def train(self):
        self.bestRules = []
        self.prevAF = 0
        
        self.rulesPruningHiThreshold = 0
        self.rulesPruningLowThreshold = 0
        
        bestRules = self.findBestRule()
        
        while self.prevAF < bestRules[0].af - 0.01:
            self.prevAF = bestRules[0].af
            # store the selected rules
            for r in bestRules:
                self.bestRules.append(r)
                
            # apply the best rule on the training set
            for r in bestRules:
                self.applyBestRule(r)
            
            self.writeRules(os.path.join(self.tmpData,'rules.txt'))
            self.writePickle(os.path.join(self.tmpData,'rules.pickle'))

            bestRules = self.findBestRule()
            
