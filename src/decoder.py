#!/usr/bin/env python2.5

from string import *
import re, pickle
from copy import *
from collections import *
from math import *

from utils import *
from slot import *
from dialogueAct import *
from rule import *
from slotDatabase import *

class DecoderData:
    pass

class Decoder:
    def __init__(self, trgCond=None):
        self.trgCond = trgCond
        self.db = SlotDatabase()
        return

    def loadDB(self, dir):
        self.db.loadTAB(dir)

    def loadData(self, inputFile, pruneSingletons = False):
        self.das = []
        self.gramIDF = defaultdict(int)
        
        # read the training data
        # build all DAs
        sem = file(inputFile, 'r')
        semLines = sem.readlines()
        
        if self.trgCond['useDeps'] == 1:
            dep = file(inputFile+'.dep', 'r')
            depLines = dep.readlines()

        for (i, line) in enumerate(semLines):
            splt = split(line, '<=>')
            sentence = strip(splt[0])
            da = strip(splt[1])

            if len(sentence) == 0 or len(da) == 0:
                continue
            
            if self.trgCond['useDeps'] == 0:
                da = DialogueAct(da, sentence, '', self.db, self.trgCond)
            else:
                da = DialogueAct(da, sentence, depLines[i], self.db, self.trgCond)
                
            da.parse()
            da.replaceDBItems()
            da.genGrams(self.gramIDF)
    
            self.das.append(da)
        

        if pruneSingletons:
            self.remGrams = [g for g in self.gramIDF if self.gramIDF[g] == 1]
                
##        f = file('removedGrams.txt', 'w')
##        for i, g in enumerate(self.remGrams):
##            f.write('%d %s\n' % (i, g))
##        f.close()
        
            # delete all singleton grams from grams in DAs
            # search for rules will be faster 
            for da in self.das:
                ret = da.removeGrams(self.remGrams)
                
                for rg in ret:
                    # I do not have to search for rg gram because it was already deleted
                    # it was a singleton.
                    self.remGrams.remove(rg)
        
        return
        
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

    def writeAlignment(self, fn):
        f = file(fn, 'w')
        
        for each in self.das:
            f.write('Text:          %s\n' % each.renderText())
            f.write('DB Text:       %s\n' % each.normText)
            
            if hasattr(each, 'valueDictPositions'):
                for k, v in sorted(each.valueDictPositions.items()):
                    f.write('Subst value:   %s => %s\n' % (k, v))
                
            each.writeAlignment(f)
            
            f.write('HYP Semantics: %s\n' % each.renderTBED(False))
            f.write('HYP Semantics: %s\n' % each.renderTBED(True))
            f.write('REF Semantics: %s\n' % each.renderCUED(False))
            f.write('REF Semantics: %s\n' % each.renderCUED(True))
            f.write('='*80+'\n')
            
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
        
        dd.bestRules = self.bestRules
        dd.trgCond = self.trgCond
        
        f = file(fn,'wb')
        pickle.dump(dd, f)
        f.close()

    def analyzeRules(self):
        print 'Number of read rules:     ', len(decoder.bestRules)
        print 'Number of unique rules:   ', len(set(decoder.bestRules))
        
        compresedRules = []
        
        for r in decoder.bestRules:
            r = deepcopy(r)
            # modify trigger gram
            if r.trigger.gram != None:
                g = list(r.trigger.gram)
                for i, w in enumerate(g):
                    if w.startswith('sv_'):
                        g[i] = re.sub('-\d+', '', w)
                
                r.trigger.gram = tuple(g)
                
            # modify trigger slots
            if r.trigger.slots != None:
                for i, s in enumerate(r.trigger.slots):
                    if s.value.startswith('sv_'):
                        r.trigger.slots[i].value = re.sub('-\d+', '', s.value)
                
            # modify trans
            if r.transformation.addSlot != None:
                if r.transformation.addSlot.value.startswith('sv_'):
                    r.transformation.addSlot.value = re.sub('-\d+', '', r.transformation.addSlot.value)
                
            if r.transformation.delSlot != None:
                if r.transformation.delSlot.value.startswith('sv_'):
                    r.transformation.delSlot.value = re.sub('-\d+', '', r.transformation.delSlot.value)
                
            if r not in compresedRules:
                compresedRules.append(r)
               
        print 'Number of compresed rules:', len(set(compresedRules))
        
        # print rules
        f = file('rules.compresed.txt','w')
        for i in range(len(compresedRules)):
            f.write(compresedRules[i].write(i))
        f.close
    
    @classmethod
    def readDecoderPickle(cls, fn):
        f = file(fn, 'rb')
        dd = pickle.load(f)
        f.close()
        
        decoder = cls()
        decoder.bestRules = dd.bestRules
        decoder.trgCond = dd.trgCond
        
        # print rules
        f = file('rules.filtered.txt','w')
        a = [x for x in decoder.bestRules if x.transformation.addSlot != None]
        d = [x for x in decoder.bestRules if x.transformation.delSlot != None]
        s = [x for x in decoder.bestRules if x.transformation.subSlot != None]
        
        for i in range(len(a)):
            f.write(a[i].write(i))
        for i in range(len(d)):
            f.write(d[i].write(i))
        for i in range(len(s)):
            f.write(s[i].write(i))
            
        f.close
        
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
        
    def writeAnalyze(self, fn):
        f = file(fn, 'w')
        
        incorrectTbed = []
        dats = defaultdict(list)
        missingSlots = defaultdict(list)
        extraSlots = defaultdict(list)
        substitutedSlots = defaultdict(dlist_factory)
        
        for each in self.das:
            if each.incorrectTbed():
                incorrectTbed.append(each)
        
        for each in incorrectTbed:
            each.getErrors(dats, missingSlots, extraSlots, substitutedSlots)

        f.write('Global statistics\n')
        f.write('='*80+'\n')
        
        f.write('   Average number of applied rules: %3.1f\n' % (sum([len(x.ruleTracker) for x in self.das])*1.0/len(self.das),))
        
        f.write('   Dialogue act type substitutions: %3d Avg per DAT type: %d\n' % ( sum([len(x) for x in dats.itervalues()]), sum([len(x) for x in dats.itervalues()])*1.0/len(dats)))
        f.write(' Missing slot items (recall error): %3d Avg per MSI type: %d\n' % (sum([len(x) for x in missingSlots.itervalues()]), sum([len(x) for x in missingSlots.itervalues()])*1.0/len(extraSlots)))
        f.write('Extra slot items (precision error): %3d Avg per ESI type: %d\n' % ( sum([len(x) for x in extraSlots.itervalues()]), sum([len(x) for x in extraSlots.itervalues()])*1.0/len(extraSlots)))

        numberOfSubstitutionsA = 0
        numberOfSubstitutions = 0
        for mi, eis in sorted(substitutedSlots.iteritems()):
            for ei, v in sorted(eis.iteritems()):
                numberOfSubstitutions += 1
                numberOfSubstitutionsA += len(v)
        if numberOfSubstitutions != 0:
            d = numberOfSubstitutionsA/numberOfSubstitutions
        else:
            d = 0.0
        f.write('                Substitution pairs: %3d Avg per SP type: %d\n' % ( numberOfSubstitutions, d))
        
        f.write('-'*80+'\n')
        kv = missingSlots.items()
        kv = [(k.renderCUED(False),len(v)) for k,v in kv]
        kv.sort()
        for k, v in kv:
            f.write('Missing slot item: %50s Occurence: %d\n' %(k, v))
        f.write('-'*80+'\n')
        
        kv = extraSlots.items()
        kv = [(k.renderTBED(False, None, None),len(v)) for k,v in kv]
        kv.sort()
        for k, v in kv:
            f.write('Extra slot item:   %50s Occurence: %d\n' %(k, v))
        f.write('-'*80+'\n')
        
        f.write('SP: %50s    %50s \n' %('REF', 'HYP'))
        me = substitutedSlots.items()
        me = [(m.renderCUED(False),es) for m,es in me]
        me.sort()
        for mi, eis in me:
            eis = eis.items()
            eis = [(ei.renderTBED(False, None, None),len(v)) for ei,v in eis]
            eis.sort()
            for ei, v in eis:
                f.write('SP: %50s => %50s Occurence: %d\n' %(mi, ei, v))

        f.write('\n')
        f.write('*'*80+'\n')
        f.write('Confused dialogue act types\n')
        f.write('*'*80+'\n\n')
        
        for k, v in sorted(dats.iteritems()):
            f.write('Confusions for: %s Occurence: %d\n' %(k, len(v)))
            f.write('='*80+'\n')
            for each in v:
                self.writeAnalyzeDA(f, each)
            
        f.write('*'*80+'\n')
        f.write('Missing slot items (recall error)\n')
        f.write('*'*80+'\n\n')
        
        for k, v in sorted(missingSlots.iteritems()):
            f.write('Missing slot item: %s Occurence: %d\n' %(k.renderCUED(True), len(v)))
            f.write('='*80+'\n')
            for each in v:
                self.writeAnalyzeDA(f, each)

        f.write('*'*80+'\n')
        f.write('Extra slot items (precision error)\n')
        f.write('*'*80+'\n\n')
        
        for k, v in sorted(extraSlots.iteritems()):
            f.write('Extra slot item: %s Occurence: %d\n' %(k.renderTBED(False, None, None), len(v)))
            f.write('='*80+'\n')
            for each in v:
                self.writeAnalyzeDA(f, each)
                
        f.write('*'*80+'\n')
        f.write('Substituted slot items (precision error)\n')
        f.write('*'*80+'\n\n')

        for mi, eis in sorted(substitutedSlots.iteritems()):
            for ei, v in sorted(eis.iteritems()):
                f.write('Substituted slot item: %s => %s Occurence: %d\n' %(mi.renderCUED(False), ei.renderTBED(False, None, None), len(v)))
                f.write('='*80+'\n')
                for each in v:
                    self.writeAnalyzeDA(f, each)

        f.close()

    def writeAnalyzeDA(self, f, each):
        f.write('Text:          %s\n' % each.renderText())
        f.write('DB Text:       %s\n' % each.normText)
        
        if hasattr(each, 'valueDictPositions'):
            for k, v in sorted(each.valueDictPositions.items()):
                f.write('Subst value:   %2d => %30s = %s\n' % (k, v, each.words[k]))
                
        each.writeAlignment(f)
        
        f.write('HYP Semantics: %s\n' % each.renderTBED(False))
        f.write('HYP Semantics: %s\n' % each.renderTBED(True))
        f.write('REF Semantics: %s\n' % each.renderCUED(False))
        f.write('REF Semantics: %s\n' % each.renderCUED(True))
        
        f.write('AppliedRules:  %d\n' % len(each.ruleTracker))
        for r in each.ruleTracker:
            f.write('%s\nDA:AFTER:THE:RULE: %s\n\n' % r)
        
        f.write('-'*80+'\n')
        
        
