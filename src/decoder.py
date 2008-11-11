#!/usr/bin/env python2.5

from string import *
import re, pickle
from copy import *
from collections import *

from utils import *
from slot import *
from dialogueAct import *
from rule import *
from slotDatabase import *

class DecoderData:
    pass

class Decoder:
    def __init__(self, trgCond=None):
        self.vocabulary = adict()
        self.trgCond = trgCond
        self.db = SlotDatabase()
        return

    def loadDB(self, dir):
        self.db.loadTAB(dir)

    def loadData(self, inputFile):
        self.das = []
        # read the training data
        # build all DAs
        sem = file(inputFile, 'r')
        semLines = sem.readlines()

        for line in semLines:
            splt = split(line, '<=>')
            sentence = strip(splt[0])
            da = strip(splt[1])

            if len(sentence) == 0 or len(da) == 0:
                continue
    
            da = DialogueAct(da, sentence, self.vocabulary, self.db, self.trgCond)
            da.parse()
            da.replaceDBItems()
            da.genGrams()
    
            self.das.append(da)
                
        return

    def loadTbedData(self, inputFile):
        # read the training data
        # build all DAs
        sem = file(inputFile, 'r')
        semLines = sem.readlines()

        for i in range(len(semLines)):
            splt = split(semLines[i], '<=>')
            sentence = strip(splt[0])
            da = strip(splt[1])

            if len(sentence) == 0 or len(da) == 0:
                continue
    
            self.das[i].parseTbed(da, sentence)
        
    def decode(self, nRules=-1):
        dcdRules = self.bestRules[:nRules]
        
        for da in self.das:
            for rule in dcdRules:
                rule.apply(da)
    
    def writeOutput(self, fn):
        f = file(fn, 'w')
        
        for da in self.das:
            f.write('%s <=> %s\n' % (da.renderText(), da.renderTBED()))
        
        f.close()

    def writeOrangeTab(self, fn):
        grams = defaultdict(int)
        for da in self.das:
            for g in da.grams:
                grams[g] += len(da.grams[g])

        gr = []
        for g in grams:
            if grams[g] >=4:
                gr.append(g)
        
        grams = sorted(gr)

        slotItems = defaultdict(int)
        for da in self.das:
            for si in da.slots:
                slotItems[si.name] += 1
                
        sis = []
        for si in slotItems:
            if si == "":
                continue
                
            if slotItems[si] >=4:
                sis.append(si)
        
        slotItems = sorted(sis)
        slotItems = ['name', 'addr', 'near'] 
        
        f = file(fn, 'w')
        f.write('c#dat')
        for g in grams:
            s = str(g).replace('"', "'").replace("', '", '-').replace('(', '').replace(')', '').replace("'", '').replace(",", '')
            f.write('\tC#'+s)
        for si in slotItems:
            s = str(si).replace('"', "'").replace("', '", '-').replace('(', '').replace(')', '').replace("'", '').replace(",", '')
            f.write('\tC#si_'+s)
        f.write('\n')
            
        for da in self.das:
            f.write(da.speechAct)
            for g in grams:
                if da.grams.has_key(g):
                    f.write('\t'+str(len(da.grams[g])))
                else:
                    f.write('\t0')
            for si in slotItems:
                c = 0
                for i in range(len(da.slots)):
                    if da.slots[i].name == si:
                        c +=1
                        
                f.write('\t'+str(c))
            f.write('\n')
        
        f.close()
        
    def writeDecoderPickle(self, fn):
        dd = DecoderData()
        
        dd.vocabulary = self.vocabulary
        dd.bestRules = self.bestRules
        dd.trgCond = self.trgCond
        
        f = file(fn,'wb')
        pickle.dump(dd, f)
        f.close()
    
    @classmethod
    def readDecoderPickle(cls, fn):
        f = file(fn, 'rb')
        dd = pickle.load(f)
        f.close()
        
        decoder = cls()
        decoder.vocabulary = dd.vocabulary
        decoder.bestRules = dd.bestRules
        decoder.trgCond = dd.trgCond
        
        return decoder
        
    def writeBestRulesPickle(self, fn):
        f = file(fn,'wb')
        pickle.dump(self.bestRules, f)
        f.close()
    
    def readBestRulesPickle(self, fn, nRules = 0):
        f = file(fn, 'rb')
        self.bestRules = pickle.load(f)
        f.close()
        
        n = len(self.bestRules)
        
        if nRules:
            self.bestRules = self.bestRules[:nRules]
            
        return n

    def writeVocabulary(self, fn):
        self.vocabulary.write(fn)
        
    def readVocabulary(self, fn):
        self.vocabulary = self.vocabulary.read(fn)
        
    def writeBestRulesTXT(self, fn):
        # print rules
        f = file(fn,'w')
        for i in range(len(self.bestRules)):
            f.write(self.bestRules[i].write(i))
        f.close
        
    def readBestRulesRulesTXT(self, fn):
        f = file(fn, 'r')
        
        lines = f.readlines()
        nLines = zip(range(len(lines)), lines)
        nRules = filter(lambda r: r[1].startswith('Rule:') != 0, nLines)
        
        for i in range(1, len(nRules)):
            rule = Rule.read(nLines[nRules[i-1][0]+1:nRules[i][0]])
        
        f.close()
        
        return
        
    def analyze(self):
        incorrectTbed = []
        dats = defaultdict(list)
        missingSlots = defaultdict(list)
        extraSlots = defaultdict(list)
        
        for each in self.das:
            if each.incorrectTbed():
                incorrectTbed.append(each)
        
        for each in incorrectTbed:
            each.getErrors(dats, missingSlots, extraSlots)

        print '*'*80
        print 'Confused dialogue act types'
        print '*'*80
        print 
        for k, v in sorted(dats.iteritems()):
            print 'Confusions for:', k, 'Occurence:' , len(v)
            print '='*80
            for each in v:
                print 'Text:         ', each.text
                print 'HYP Semantics:', each.renderTBED()
                print 'REF Semantics:', each.renderCUED()
                print '-'*80
            
        print '*'*80
        print 'Missing slot items (recall error)'
        print '*'*80
        print 
        for k, v in sorted(missingSlots.iteritems()):
            print 'Missing slot item:', k, 'Occurence:' , len(v)
            print '='*80
            for each in v:
                print 'Text:         ', each.text
                print 'HYP Semantics:', each.renderTBED()
                print 'REF Semantics:', each.renderCUED()
                print '-'*80

        print '*'*80
        print 'Extra slot items (precision error)'
        print '*'*80
        print 
        for k, v in sorted(extraSlots.iteritems()):
            print 'Extra slot item:', k, 'Occurence:' , len(v)
            print '='*80
            for each in v:
                print 'Text:         ', each.text
                print 'HYP Semantics:', each.renderTBED()
                print 'REF Semantics:', each.renderCUED()
                print '-'*80

        print 'Global statistics'
        print '='*80
        print '   Dialogue act type substitutions:', sum([len(x) for x in dats.itervalues()]), 'Avg per DAT type:', sum([len(x) for x in dats.itervalues()])*1.0/len(dats)
        print ' Missing slot items (recall error):', sum([len(x) for x in missingSlots.itervalues()]), 'Avg per MSI type:', sum([len(x) for x in missingSlots.itervalues()])*1.0/len(extraSlots)
        print 'Extra slot items (precision error):', sum([len(x) for x in extraSlots.itervalues()]), 'Avg per ESI type:', sum([len(x) for x in extraSlots.itervalues()])*1.0/len(extraSlots)

        return
