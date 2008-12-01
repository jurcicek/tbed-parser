#!/usr/bin/env python2.5

import re
from string import *
from copy import *
from collections import *

from utils import *
from slot import *
from transformation import *
from trigger import *
      
class DialogueAct:
    def __init__(self, cuedDA, text, vocabulary, db, settings):
        # train data values
        self.cuedDA = cuedDA
        self.text = ' '.join(text.split())
        self.tbedText = ' '.join(text.split())
        self.vocabulary = vocabulary
        self.db = db
        self.settings = settings

        self.speechAct = self.vocabulary['']
        self.tbedSpeechAct = self.vocabulary['inform']
        
        self.slots = []
        self.tbedSlots = []
        
        self.valueDictCounter = defaultdict(int)
        self.valueDict = {}
        self.tbedValueDictCounter = defaultdict(int)
        self.tbedValueDict = {}
        
        # in this array I store all rules applied on the DA in 
        # the sequencial order
        self.ruleTracker = []

    def __str__(self):
        s = self.text+' - '
        s+= self.cuedDA+' - '
        s+= self.vocabulary.getKey(self.speechAct)+' - '
        s+= self.vocabulary.getKey(self.tbedSpeechAct)+' - '
        s+= str(self.slots)+' - '
        s+= str(self.tbedSlots)+' - '

        return s

    def computeBorders(self):
        '''
        This method compute borders for each slot in this dialogue act. 
        Borders of each slot definy proximity 'atrea' where the lexical 
        triggers must be triggered so that SubSlot operation chould be
        applied on particular slot.
        
        FIX: Some slot might dominate the same words; as a result, they shoud have
        the same borders. It is not implemented now.
        '''
        for each in self.tbedSlots:
            if not each.lexIndex:
                raise ValueError('Slot has lexical alignment set.')
                
            each.leftMiddle = min(each.lexIndex)
            each.rightMiddle = max(each.lexIndex)
            
        self.tbedSlots.sort(cmp=lambda x, y: cmp(x.leftMiddle, y.leftMiddle))
        
        if len(self.tbedSlots) > 0:
            self.tbedSlots[0].leftBorder = 0
            for i in range(1, len(self.tbedSlots)):
                self.tbedSlots[i].leftBorder = self.tbedSlots[i-1].rightMiddle+1
            
            for i in range(0, len(self.tbedSlots)-1):
                self.tbedSlots[i].rightBorder = self.tbedSlots[i+1].leftMiddle-1
                    
            self.tbedSlots[-1].rightBorder = len(self.words)-1
            
            for i in range(len(self.tbedSlots)):
                if self.tbedSlots[i].leftBorder > self.tbedSlots[i].leftMiddle:
                    self.tbedSlots[i].leftBorder = self.tbedSlots[i].leftMiddle
                if self.tbedSlots[i].rightBorder < self.tbedSlots[i].rightMiddle:
                    self.tbedSlots[i].rightBorder = self.tbedSlots[i].rightMiddle
            
##        print '+'*80
##        print self.text
##        for each in self.tbedSlots:
##            print each.renderCUED(), each.leftBorder, each.leftMiddle, each.rightMiddle, each.rightBorder

    def writeAlignment(self, f):
        f.write('.'*80+'\n')
        f.write(' '.join(['%s'  % w for w in self.words])+'\n')
        f.write(' '.join(['%*d' % (len(w), i) for i, w in enumerate(self.words)])+'\n')
            
        for each in self.tbedSlots:
            numberOfLeftDots = sum([len(w)+1 for i, w in enumerate(self.words) if i < each.leftBorder])
            numberOfLeftDashes = sum([len(w)+1 for i, w in enumerate(self.words) if i >= each.leftBorder and i<each.leftMiddle])
            numberOfEquals = sum([len(w)+1 for i, w in enumerate(self.words) if i >= each.leftMiddle and i<=each.rightMiddle])
            numberOfRightDashes = sum([len(w)+1 for i, w in enumerate(self.words) if i > each.rightMiddle and i<=each.rightBorder])
            numberOfRightDots = sum([len(w)+1 for i, w in enumerate(self.words) if i > each.rightBorder])
            f.write(' '*numberOfLeftDots)
            f.write('-'*numberOfLeftDashes)
            f.write('='*numberOfEquals)
            f.write('-'*numberOfRightDashes)
            f.write(' '*numberOfRightDots+'\n')
            
            f.write('%50s (%.2d,%.2d,%.2d,%.2d) <= %s\n' % (each.renderTBED(False, self.valueDictPositions, self.words), each.leftBorder, each.leftMiddle, each.rightMiddle, each.rightBorder, str(sorted(each.lexIndex))))
        f.write('.'*80+'\n')

    def parseDA(self, cuedDA, text):
        numOfDAs = len(splitByComma(cuedDA))
        if numOfDAs > 1:
            raise ValueError('Too many DAs in input text.')

        # get the speech-act
        i = cuedDA.index("(")
        speechAct = self.vocabulary[cuedDA[:i]]
        slots = cuedDA[i:].lower()
        slots = slots.replace('(', '')
        slots = slots.replace(')', '')
        
        slts = []
        if slots == '':
            # no slots to process
            slots = []
        else:
            # Francois's hack:
            slots = slots.replace('.!=', '!=').replace('zeroProb-','')
            
            # split slots
            slots = splitByComma(slots)
            for slt in slots:
                try:
                    s = Slot(slt)
                    s.parse()
                    slts.append(s)
                except ValueError:
                    # check for Francois invalid slot items
                    pass

        return speechAct, slts

    def parse(self):
        self.speechAct, self.slots = self.parseDA(self.cuedDA, self.text)
    
    def parseTbed(self, cuedDA, text):
##        if text != self.text:
##            raise ValueError('Loaded tbed text must equal to the training text.')
            
        self.tbedSpeechAct, self.tbedSlots = self.parseDA(cuedDA, text)
    
    def replaceSV(self, text, sn, sv, i):
        return text[0:i]+sn+text[i+len(sv):]
        
    def replaceDBItems(self):
        """
        This method replace all lexical ralizations of database items
        by some tags in form 'sv_slotname-N', where N is counter of occurence in 
        the sentence. There is a problem if some slot value occures in different 
        slots (names). Than only one association is made in greedy manner. 
        
        There is also another issue with db items. Some words are replaced 
        although they are not db items. For example a word 'one' is replaced by 
        'sv-stars-1' in sentence 'I would like this one', which is apparently 
        wrong.
        """
                
        if self.settings == None:
            return
            
        if self.settings['DBItems'] != 'replace':
            return
        
        f = file('dbItemsReplacement.txt', 'a')
        f.write('#'*80+'\n')
        f.write('Text:         '+ self.text+'\n')
        
        for (sn, sv, svs, c, cc) in self.db.values:
            while True:
                i = self.text.find(svs)
                if i != -1:
                    # test wheather there are spaces around the word. that it is not a 
                    # substring of another word!
                    if i > 0 and self.text[i-1] != ' ':
                        break
                    if i < len(self.text)-len(svs) and self.text[i+len(svs)] != ' ':
                        break
                            
                    # I found the slot value synonym from database in the 
                    # sentence, I must replace it
                    newSV1 = 'sv_'+sn
                    self.valueDictCounter[newSV1] += 1
                    newSV2 = newSV1+'-'+str(self.valueDictCounter[newSV1])
                    self.valueDict[newSV2] = (sv, svs)
                    
                    self.text = self.replaceSV(self.text, newSV2, svs, i)

                    # find slot which match
                    for slt in self.slots:      
##                        if slt.name.endswith(sn) and slt.value in self.db[sn][sv]:
                        # I do not check wheter there is the same name of the slot name
                        # for the substituted  slot value. If I chose a wrong slot
                        # value label, I have to lear how to fix it
                        if slt.value in self.db[sn][sv]:
                            slt.origValue = slt.value
                            slt.value = newSV2
                            break
                else:
                    break

        self.words = split(self.text)
        self.words = [self.vocabulary[w] for w in self.words]
        
        # now I have to get rid of indexes and create dictionary
        # with positions and correct slot values
        
        self.valueDictPositions = {}
        for i, w in enumerate(self.words):
            if w.startswith('sv_'):
                self.valueDictPositions[i] = self.valueDict[w]

##        print self.text
##        r = re.compile('\w+-\d+')
##        pos = 0
##        while True:
##            m = r.search(self.text, pos)
##            if m == None:
##                break
##            pos = m.end()
##            print m.start(), m.end(), self.text[m.start():m.end()]
##        
        
        self.words = split(self.text)
        self.words = [self.vocabulary[w] for w in self.words]

        sv_count = {}
        sv_map = {}
        for p in sorted(self.valueDictPositions):
            sv_count[self.words[p][:-2]] = 0
        for p in sorted(self.valueDictPositions):
            sv_map[self.words[p]] = self.words[p][:-2]+'-'+str(sv_count[self.words[p][:-2]] % 2)
            sv_count[self.words[p][:-2]] += 1
            
##        print '-'*80
##        print self.text
####        print sv_count
##        print sv_map
####        print
##        
##        for p in sorted(self.valueDictPositions):
##            print p, self.words[p], sv_map[self.words[p]], self.valueDictPositions[p]
        
        # update self.words
        for i, w in enumerate(self.words): 
            if w.startswith('sv_'):
                self.words[i] = sv_map[w]
        # as a result, I have to update text        
        self.text = ' '.join(self.words)
        
        # update slot values
##        print self.renderCUED()
        for slt in self.slots:      
            if slt.value in sv_map:
                slt.value = sv_map[slt.value]
        
##        print self.text
##        print self.renderCUED()
        
        
##        self.text = re.sub('-\d+','',self.text)
##        self.words = split(self.text)
##        self.words = [self.vocabulary[w] for w in self.words]
        
        for k, v in sorted(self.valueDictPositions.items()):
            f.write('Subst value:  %2d => %30s = %s\n' % (k, v, self.words[k]))
        f.write('DB Text:      '+ self.text+'\n')
        f.write('Slots:        '+ str([x.renderCUED(False) for x in self.slots]))
        f.write('\n')
        f.close()
        

    def replaceDBItemsTbed(self):
        ''' I guess that this metyhod is not neded anymmore.'''
        
        if self.settings == None:
            return
            
        if self.settings['DBItems'] != 'replace':
            return
        
##        f = file('log.txt', 'a')
##        f.write('#'*80+'\n')
        
        for (sn, sv, svs, c, cc) in self.db.values:
            while True:
                i = self.tbedText.find(svs)
                if i != -1:
                    # test wheather there are spaces around the word. that it is not a 
                    # substring of another word!
                    if i > 0 and self.tbedText[i-1] != ' ':
                        break
                    if i < len(self.tbedText)-len(svs) and self.tbedText[i+len(svs)] != ' ':
                        break
                            
                    # I found the slot value synonym from database in the 
                    # sentence, I must replace it
                    newSV = 'sv_'+sn
                    self.tbedValueDictCounter[newSV] += 1
##                    newSV = newSV+'-'+str(self.tbedValueDictCounter[newSV])
                    self.tbedValueDict[newSV] = (sv, svs)
                    
                    self.tbedText = self.replaceSV(self.tbedText, newSV, svs, i)

                    # find slot which match
                    for slt in self.tbedSlots:      
##                        if slt.name.endswith(sn) and slt.value in self.db[sn][sv]:
                        # I do not check wheter there is the same name of the slot name
                        # for the substituted  slot value. If I chose a wrong slot
                        # value label, I have to lear how to fix it
                        if slt.value in self.db[sn][sv]:
                            slt.origValue = slt.value
                            slt.value = newSV
                            break
                else:
                    break
        
    def genGrams(self):
        if not hasattr(self, 'settings'):
            return
        
        if not hasattr(self, 'word'):
            # I did not run replaceDBItems(); as a result, I have to split text
            self.words = split(self.text)
            self.words = [self.vocabulary[w] for w in self.words]
        
        self.grams = defaultdict(set)
        # generate unigrams, bigrams, and trigrams from text
        for i in range(len(self.words)):
            self.grams[(self.words[i],)].add((i,i))
        
        if self.settings['nGrams'] >=2:
            for i in range(1, len(self.words)):
                self.grams[(self.words[i-1],self.words[i])].add((i-1, i))
        if self.settings['nGrams'] >=3:
            for i in range(2, len(self.words)):
                self.grams[(self.words[i-2],self.words[i-1],self.words[i])].add((i-2,i))
        if self.settings['nGrams'] >=4:
            for i in range(3, len(self.words)):
                self.grams[(self.words[i-3],self.words[i-2],self.words[i-1],self.words[i])].add((i-3,i))

        if self.settings['nStarGrams'] >=3:
            for i in range(2, len(self.words)):
                self.grams[(self.words[i-2],'*1',self.words[i])].add((i-2, i))
        if self.settings['nStarGrams'] >=4:
            for i in range(3, len(self.words)):
                self.grams[(self.words[i-3],'*2',self.words[i])].add((i-3, i))
        if self.settings['nStarGrams'] >=5:
            for i in range(4, len(self.words)):
                self.grams[(self.words[i-4],'*3',self.words[i])].add((i-4, i))
        
    def renderCUED(self, origSV=False):
        DA = self.vocabulary.getKey(self.speechAct)
        rendered_slots = ','.join([each_slot.renderCUED(origSV) for each_slot in self.slots])
        DA += '('+rendered_slots+')'

        return DA
        
    def renderTBED(self, origSV = True):
        DA = self.vocabulary.getKey(self.tbedSpeechAct)
        rendered_slots = [each_slot.renderTBED(origSV, self.valueDictPositions,self.words) for each_slot in self.tbedSlots]
        
        # I filter out sequencial duplicities among slot
        # in other words on the output of the parser cannot be two same slots behind each 
        # other => must be true: slts[i] != slts[i+1]
        rendered_slots_filtered = []
        if len(rendered_slots) > 0:
            rendered_slots_filtered.append(rendered_slots[0])
            for slt in rendered_slots[1:]:
                if slt != rendered_slots_filtered[-1]:
                    rendered_slots_filtered.append(slt)
                
        DA += '('+','.join(rendered_slots_filtered)+')'
        
        return DA

    def renderText(self):
        ws=[]
        for i, ew in enumerate(self.words):
            if i in self.valueDictPositions:
                ws.append(self.valueDictPositions[i][1])
            else:
                ws.append(ew)
        return ' '.join(ws)
        
    def getNumOfSlots(self):
        return len(self.slots)
        
    def measure(self):
        # get similarity measure
        if self.tbedSpeechAct == self.speechAct:
            Ha = 1
        else:
            Ha = 0
            
        Na = 1
        
        # slots measures
        Hi = len(self.tbedSlots&self.slots)
        Ri = len(self.tbedSlots)
        Ni = len(self.slots)
            
        return (Ha, Na, Hi, Ri, Ni)

    def incorrectTbed(self):
        if self.speechAct != self.tbedSpeechAct or self.slots != self.tbedSlots:
            return True
        
        return False
    
    def getErrors(self, dats, missingSlots, extraSlots, substitutedSlots):
        if self.speechAct != self.tbedSpeechAct:
            dats[self.speechAct].append(self)
            
        for each in self.getMissingSlotItems():
            missingSlots[each].append(self)
        for each in self.getExtraSlotItems():
            extraSlots[each].append(self)
        
        for mi in self.getMissingSlotItems():
            for ei in self.getExtraSlotItems():
                if mi.value == ei.value:
                    substitutedSlots[mi][ei].append(self)
                    
        return
    
    def getMissingSlotItems(self):
        msi = []
        for si in self.slots:
            if si not in self.tbedSlots:
                msi.append(si)
        return msi
    
    def getExtraSlotItems(self):
        esi = []
        for si in self.tbedSlots:
            if si not in self.slots:
                esi.append(si)
        return esi
        
    def genTrans(self):
        # return a set of all posible modifications of the current DA
        # I use the dictionary to measure how many times the transformation
        # can be potentinaly usevul for this DA. Most of teh time the value 
        # will be equal zero but of DAs it might be different. 
        # If I estimate occurences properly. I can sort rules more preciselly.
        trans = defaultdict(int)
        
        # speech acts
        # return transformation for speech act only if the 
        # tbedSpeechAct is wrong
        if self.speechAct != self.tbedSpeechAct:
            trans[Transformation(speechAct=self.speechAct)] += 1
        
        # slot & values
        # return transformation for slot & value only if the 
        # the slot&value is missing or is it should not be here is wrong
        # self.tbedSlots array is list which we update (improve)
        missingSlotItems = self.getMissingSlotItems()
        extraSlotItems = self.getExtraSlotItems()
        
        for slot in missingSlotItems:
            trans[Transformation(addSlot=slot)] += 1 
            
        for slot in extraSlotItems:
            trans[Transformation(delSlot=slot)] += 1 

        for extraSlot in extraSlotItems:
            for missingSlot in missingSlotItems:
                # allow to substitute the equal sign
##                if extraSlot.equal != missingSlot.equal and extraSlot.value == missingSlot.value:
                if extraSlot.equal != missingSlot.equal:
                    es = deepcopy(extraSlot)
                    ms = deepcopy(missingSlot)
                    es.name  = None
                    es.value = None
                    ms.name  = None
                    ms.value = None
                        
                    trans[Transformation(subSlot=(es, ms, 'left'))] += 1 
                    
                # allow to substitute the name
                if extraSlot.name != missingSlot.name:
                    es = deepcopy(extraSlot)
                    ms = deepcopy(missingSlot)
                    es.equal = None
                    es.value = None
                    ms.equal = None
                    ms.value = None
                        
                    trans[Transformation(subSlot=(es, ms, 'left'))] += 1 
        
        for t in trans:
            t.occurence += trans[t]
            
        # do not explode transformations, only one modification 
        # at one time is allowed
        
        return set(trans.keys())
        
    def genTriggers(self):
        # collect all posible triggers for all dimmensions 
        #   (speechAct, grams, slots)
        # a gram must be always part of the trigger
        
        saCond = [None,]
        if self.settings['speechAct'] >=1:
            saCond.append(self.tbedSpeechAct)
        
        slotsCond = [None,]
        if self.settings['nSlots'] >= 1:
            for slot in self.tbedSlots:
                slotsCond.append([deepcopy(slot),])
                
            if self.settings['nSlots'] >= 2:
                ts = list(self.tbedSlots)
                for i in range(len(ts)):
                    for j in range(i+1, len(ts)):
                        slotsCond.append([deepcopy(ts[i]),deepcopy(ts[j])])

        # sentece length trigger
        lengthCond = [None,]
        if self.settings['lngth'] >= 1:
            lengthCond.append(len(self.words))
        
        # sentece length trigger, None mean I do not care
        hasSlotsCond = [None,]
        if self.settings['hasSlots'] >= 1:
            if len(self.tbedSlots) == 0:
                hasSlotsCond.append(1) # False
            else:
                hasSlotsCond.append(2) # True
            
        # generate triggers
        triggers = set()
        # explode trigger combinations
        for sa in saCond:
            for gram in self.grams:
                for slot in slotsCond:
                    for lngth in lengthCond:
                        for hasSlots in hasSlotsCond:
                            triggers.add(
                                Trigger(speechAct=sa, 
                                        gram=gram, 
                                        slots=slot,
                                        lngth=lngth,
                                        hasSlots=hasSlots))
        
        return triggers
