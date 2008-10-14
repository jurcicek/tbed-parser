#!/usr/bin/env python2.5

import re, random, os.path
from copy import *
from string import *
from threading import *


from utils import *
from slot import *
from dialogueAct import *
from rule import *
from baseTD import *

class Trainer(BaseTD):
    def __init__(self, fos, fosa, trgCond,tmpData):
        BaseTD.__init__(self, fos = fos, fosa = fosa, trgCond = trgCond)
        self.tmpData = tmpData
        
        return

    def findBestRule(self):
        self.rules = {}
        # get all applicable rules
        for da in self.das:
            rs = getRules(da, self.trgCond)
            
            for r in rs:
                self.rules[r] = self.rules.get(r,0) + 1

        for r in self.rules:
            r.occurence = self.rules[r]
            
##        print rules.values()
        print '---------------------------------------------------------'
        print 'Number of applicable rules %d: ' % len(self.rules)
        self.rls = self.rules.keys()
##        self.rls = random.sample(self.rls, len(self.rls)/(self.iRule/2+1))
        print '                 pruned to %d: ' % len(self.rls)
        print '---------------------------------------------------------'

        self.rls.sort(cmp=lambda x,y: cmp(x.occurence, y.occurence), reverse=True)
        
        # apply each rule and measure the score
        for rule in self.rls:
            Ha = Na = Hi = Ri = Ni = 0
            for da in self.das:
                Ha += rule.measureDiff(da)
                Na += 1 
                
            prec = 0.0
            rec  = 0.0
            f    = 0.0
            acc  = 100.0*Ha/Na
            af   = acc
            
            rule.setPerformance(af, acc, f, prec, rec)
            
##            print '%s Occ:%d AF:%.2f Cplx:%d Acc:%.2f F:%.2f' % (rule, rule.occurence, af, rule.complexity(), acc, f)
##            print Ha, Na, Hi, Ri, Ni
        
        # sort rules accordin their performance and complexity
        
        self.rls.sort(cmp=lambda x,y: x.cmpPlx(y))
            
        if len(self.rls) == 0:
            print 'No applicable rules.'
            return None
        else:
            print 'Best: %s AF:%.3f Cplx:%d Occ:%d' % (self.rls[0], self.rls[0].af, self.rls[0].complexity(), self.rls[0].occurence)
            for i in range(1, min([len(self.rls), 10])):
                print ' Opt: %s AF:%.3f Cplx:%d Occ:%d' % (self.rls[i], self.rls[i].af, self.rls[i].complexity(), self.rls[i].occurence)
        
        return self.selectBestRules(self.rls[:10])

    def applyBestRule(self, bestRule):
        for da in self.das:
            bestRule.apply(da)
    
    def selectBestRules(self, bestRules):
        br = []
        br.append(bestRules[0])

        # I have to encourage increase perferomance in recall because
        # this learning is very defensive = 
        # it slowly increases the recall
        for i in range(1, len(bestRules)):
            if bestRules[i].transformation.addSlot == None:
                continue
            elif bestRules[i].af < 0:
                continue
            elif bestRules[i].transformation.addSlot == bestRules[i-1].transformation.addSlot:
                # remove duplicates
                continue
                
            br.append(bestRules[i])

##        for r in br:
##            priaccnt '<<<Slct: %s AF:%.2f Cplx:%d' % (r, r.af, r.complexity())
        
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
            print 'Slct: %s AF:%.3f Cplx:%d' % (r, r.af, r.complexity())
                
        return sr
    
    def train(self):
        self.bestRules = []
        self.prevAF = 0
        self.iRule = 0
        
        self.rulesPruningHiThreshold = 0
        self.rulesPruningLowThreshold = 0
        
        bestRules = self.findBestRule()
        
        while bestRules[0].af - 0.001 > 0:
            self.prevAF = bestRules[0].af
            # store the selected rules
            for r in bestRules:
                self.bestRules.append(r)
                
            # apply the best rule on the training set
            for r in bestRules:
                self.applyBestRule(r)
            
            self.writeRules(os.path.join(self.tmpData,'rules.txt'))
            self.writePickle(os.path.join(self.tmpData,'rules.pickle'))
            self.writeDict(os.path.join(self.tmpData,'rules.pckl-dict'))

            self.iRule += 1
            bestRules = self.findBestRule()
            
            if bestRules == None:
                break
