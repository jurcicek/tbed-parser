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
minNetScore = 2

class Trainer(Decoder):
    def __init__(self, trgCond, tmpData):
        Decoder.__init__(self, trgCond = trgCond)
        self.tmpData = tmpData
        
        return

    def genRulesFromDB(self):
        for slot_name in self.db.keys():
            for slot_value in self.db[slot_name].keys():
                for slot_value_synonym in self.db[slot_name][slot_value]:
                    slt = Slot(slot_name+'='+slot_value)
                    slt.parse()
                    trg = Trigger(gram=tuple(slot_value_synonym.split()))
                    trn = Transformation(addSlot=slt)
                    r = Rule(trg, trn)
                    self.bestRules.append(r)
                    self.applyBestRule(r)
                    self.iRule += 1
                    
    def findRuleForDAT(self):
        datStat = defaultdict(int)
        
        for da in self.das:
            datStat[da.speechAct] += 1
        
        dat = [(datStat[sa], sa) for sa in datStat]
        dat.sort(reverse = True)
        
        # return rule which assigns to dat the most common speech act
        r = Rule(Trigger(), Transformation(speechAct=dat[0][1]))
        r.netScore = minNetScore
        
        return [r,]
    
    def findBestRules(self):
        print '=================== FIND BEST START ====================='
        rules = defaultdict(int)
        trg2da = defaultdict(list)
        # get all applicable rules
        for i in xrange(len(self.das)):
            rs, ts = getRules(self.das[i], self.trgCond)
            
            # the rules can fix more than one error in one sentence but I still
            # use this simple measuere to sort them
            for r in rs:
                rules[r] += r.getOccurance()
            
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
        self.rls.sort(cmp=lambda x,y: x.cmpOcc(y), reverse=True)

        # apply each rule and measure the score
        R = 0
        maxNetScore = 0
        lastOccurence = 0
        N = len(self.das)
        for rule in self.rls:
            if lastOccurence > rule.occurence and rule.occurence < maxNetScore:
                # the best possible benefit of the rule is lower than the
                # benefit of some already tested rule. And because the rules 
                # are sorted w.r.t occurence, I can not find a better rule.
                break
            lastOccurence = rule.occurence    
            R += 1

            # compute netScore for the curent rule
            netScore = 0 
            posScore = 0
            negScore = 0
            
            for i in trg2da[rule.trigger]:
                nsp, psp, ngsp = rule.transformation.measureDiff(self.das[i], rule.trigger)
                netScore += nsp
                posScore += psp
                negScore += ngsp
            
            
##            netScore = harmonicMean(netScore, posScore/(negScore + 1))
            
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
        
        if self.trgCond['DBItems'] == 'genRules':
            self.genRulesFromDB()
        
        bestRules = self.findRuleForDAT()
        
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

            self.iRule += 1
            bestRules = self.findBestRules()
            
            if bestRules == None:
                break
