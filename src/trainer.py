#!/usr/bin/env python2.5

import re, random, os.path
from collections import *
from copy import *
from string import *
from threading import *

from utils import *
from slot import *
from dialogueAct import *
from rule import *
from decoder import *

maxOptRules = 10
minNetScore = 3

class Trainer(Decoder):
    def __init__(self, trgCond, tmpData):
        Decoder.__init__(self, trgCond = trgCond)
        self.tmpData = tmpData
        
        return

    def findBestRules(self):
        print '=================== FIND BEST START ====================='
        rules = defaultdict(int)
        trg2da = defaultdict(list)
        # get all applicable rules
        for i in xrange(len(self.das)):
            rs, ts = getRules(self.das[i], self.trgCond)
            
            for r in rs:
                rules[r] += 1
            
            for t in ts:
                # collect indexes of DAs for which the trigger satisfies the 
                # conditions. As a result I do not have to
                # call the validate function on these DAs
                trg2da[t].append(i)
            
        for r in rules:
            r.occurence = rules[r]
##            if r.transformation.subSlot:
##                print '>>> SUB ',r 
            
        print '========================================================='
        print 'Number of applicable rules: %d' % len(rules)

        self.rls = rules.keys() 
        for r in self.rls:
            if r.occurence < minNetScore:
                del rules[r]
        print '                 pruned to: %d' % len(rules)

        self.rls = rules.keys() 
        # I might delete rules it seem that I do not need it any more
        self.rls.sort(cmp=lambda x,y: cmp(x.occurence, y.occurence), reverse=True)

        # apply each rule and measure the score
        R = 0
        maxNetScore = 0
        N = len(self.das)
        for rule in self.rls:
            if rule.occurence < maxNetScore:
                # the best possible benefit of the rule is lower than the
                # benefit of some already tested rule. And because the rules 
                # are sorted w.r.t occurence, I can not find a better rule.
                break
                
            R += 1

            # compute netScore for the curent rule
            netScore = 0 
            for i in trg2da[rule.trigger]:
                netScore += rule.transformation.measureDiff(self.das[i], rule.trigger)
            
            if netScore > maxNetScore:
                maxNetScore = netScore
            
            rule.setPerformance(netScore)
            
##            print '%s netScore Occ:%d NetScore:%d Cplx:%d' % (rule, rule.occurence, netScore, rule.complexity())
        
        print '    Number of tested rules: %d ' % R
        print '========================================================='
        
        # sort the rules according their performance and complexity
        self.rls.sort(cmp=lambda x,y: x.cmpPlx(y))
            
        if len(self.rls) == 0:
            print 'No applicable rules.'
            return None
        else:
            print 'Best: %s Occ:%d NetScore:%d Cplx:%d' % (self.rls[0], self.rls[0].occurence, self.rls[0].netScore, self.rls[0].complexity())
            for i in range(1, min([len(self.rls), maxOptRules])):
                print ' Opt: %s Occ:%d NetScore:%d Cplx:%d' % (self.rls[i], self.rls[i].occurence, self.rls[i].netScore, self.rls[i].complexity())
        
        print '==================== FIND BEST END ======================'
        return self.selectBestRules(self.rls[:maxOptRules])

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
            elif bestRules[i].netScore < minNetScore:
                continue
            elif bestRules[i].transformation.addSlot == bestRules[i-1].transformation.addSlot:
                # remove duplicates
                continue
                
            br.append(bestRules[i])

##        for r in br:
##            priaccnt '<<<Slct: %s Cplx:%d' % (r, r.complexity())
        
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
            print 'Slct: %s Occ:%d NetScore:%d Cplx:%d' % (r, r.occurence, r.netScore, r.complexity())
                
        return sr
    
    def train(self):
        self.bestRules = []
        self.iRule = 0
                
        bestRules = self.findBestRules()
        
        while bestRules[0].netScore >= minNetScore:
            # store the selected rules
            for r in bestRules:
                self.bestRules.append(r)
                
            # apply the best rule on the training set
            for r in bestRules:
                self.applyBestRule(r)
            
            self.writeDecoderPickle(os.path.join(self.tmpData,'rules.pckl-decoder'))
            self.writeBestRulesTXT(os.path.join(self.tmpData,'rules.txt'))
            self.writeBestRulesPickle(os.path.join(self.tmpData,'rules.pckl-bestrules'))
            self.writeVocabulary(os.path.join(self.tmpData,'rules.pckl-vocabulary'))

            self.iRule += 1
            bestRules = self.findBestRules()
            
            if bestRules == None:
                break
