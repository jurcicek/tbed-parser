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
            
            for rule in rs:
                self.rules[rule] = self.rules.get(rule,0) + 1

##        print rules.values()
        self.rules = self.rules.keys()

        print 'Number of applicable rules %d: ' % len(self.rules)
        
        # apply each rule and measure the score
        for rule in self.rules:
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
                
            rule.setPerformance(af, acc, f)
            
##            print rule, af, acc, f
        
        # sort rules accordin their performance and complexity
        
        self.rules.sort(cmp=lambda x,y: x.cmpPlx(y))
            
        if len(self.rules) == 0:
            print 'No applicable rules.'
            return None, 0.0
        else:
            print 'Best: %s AF:%.2f Cplx:%d' % (self.rules[0], self.rules[0].af, self.rules[0].complexity())
            for i in range(1,10):
                print ' Opt: %s AF:%.2f Cplx:%d' % (self.rules[i], self.rules[i].af, self.rules[i].complexity())
        
        return self.rules[0], self.rules[0].af

    def applyBestRule(self, bestRule):
        for da in self.das:
            bestRule.apply(da)
    
    def train(self):
        self.bestRules = []
        
        prevAF = 0
        
        bestRule, af = self.findBestRule()

        while prevAF < af - 0.1:
            prevAF = af
            self.bestRules.append(bestRule)
            # apply the best rule on the training set
            self.applyBestRule(bestRule)
            
            self.writeRules(os.path.join(self.tmpData,'rules.txt'))
            self.writePickle(os.path.join(self.tmpData,'rules.pickle'))

            bestRule, af = self.findBestRule()
            
