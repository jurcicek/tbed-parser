#!/usr/bin/env python2.5

from string import *
from copy import *
import re, pickle

from utils import *
from slot import *
from dialogueAct import *
from rule import *

class BaseTD:
    def __init__(self, fos, fosa,trgCond):
        self.das = []
        self.filterOutSlots = fos
        self.filterOutSpeechActs = fosa
        self.vocabulary = adict()
        self.trgCond = trgCond


        return

    def loadData(self, inputFile, mpdas):
        # read the training data
        # build all DAs
        sem = file(inputFile, 'r')
        semLines = sem.readlines()[:mpdas]

        for line in semLines:
            splt = split(line, '<=>')
            sentence = strip(splt[0])
            da = strip(splt[1])

            if len(sentence) == 0 or len(da) == 0:
                continue
    
            da = DialogueAct(da, sentence, self.vocabulary)
            da.parse()
            da.genGrams(self.trgCond)
    
##            print da.renderCUED()
            
            # filter out some input semantics
            if da.getNumOfSlots() in self.filterOutSlots:
                continue
    
            if da.speechAct in self.filterOutSpeechActs:
                continue

            self.das.append(da)
            
        return

    def printRules(self):
        print
        print "Rules' sequence"
        for each in self.bestRules:
            print each, 'Acc:', each.acc, 'F:', each.f
        
        return
            
    def writeRules(self, fn):
        # print rules
        f = file(fn,'w')
        
        for i in range(len(self.bestRules)):
            f.write(self.bestRules[i].write(i))
            
        f.close
            
        return
        
    def writePickle(self, fn):
        f = file(fn,'wb')
        pickle.dump(self.bestRules, f)
        f.close()
        return
    
    def readPickle(self, fn):
        f = file(fn, 'rb')
        self.bestRules = pickle.load(f)
        f.close()
        return

    def writeDict(self, fn):
        self.vocabulary.write(fn)
        
    def readDict(self, fn):
        self.vocabulary = self.vocabulary.read(fn)
        
    def readRules(self, fn):
        f = file(fn, 'r')
        
        lines = f.readlines()
        nLines = zip(range(len(lines)), lines)
        nRules = filter(lambda r: r[1].startswith('Rule:') != 0, nLines)
        
        for i in range(1, len(nRules)):
            rule = Rule.read(nLines[nRules[i-1][0]+1:nRules[i][0]])
        
        f.close()
        
        return

    def applyBestRule(self, bestRule):
        for da in self.das:
            bestRule.apply(da)
