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
        self.vocabulary = vocabulary
        self.db = db
        self.settings = settings

        self.speechAct = self.vocabulary['']
        self.tbedSpeechAct = self.vocabulary['inform']
        
        self.slots = []
        self.tbedSlots = []
        
        self.valueDictCounter = defaultdict(int)
        self.valueDict = {}

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
            each.leftMiddle = min(each.lexIndex)
            each.rightMiddle = max(each.lexIndex)
            
        self.tbedSlots.sort(cmp=lambda x, y: cmp(x.leftMiddle, y.leftMiddle))
        
        if len(self.tbedSlots) > 0:
            self.tbedSlots[0].leftBorder = 0
            for i in range(1, len(self.tbedSlots)):
                    self.tbedSlots[i].leftBorder = self.tbedSlots[i-1].rightMiddle
            
            for i in range(0, len(self.tbedSlots)-1):
                    self.tbedSlots[i].rightBorder = self.tbedSlots[i+1].leftMiddle
            self.tbedSlots[-1].rightBorder = len(self.words)
        
##        print '+'*80
##        print self.text
##        for each in self.tbedSlots:
##            print each.renderCUED(), each.leftBorder, each.leftMiddle, each.rightMiddle, each.rightBorder
            
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
        if text != self.text:
            raise ValueError('Loaded tbed text must equal to the training text.')
            
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
        
        for (sn, sv, svs, c) in self.db.values:
            i = self.text.find(svs)
            # test wheether there are sspaces around the word, that it is not a 
            # substring of another word
            if i > 0 and self.text[i-1] != ' ':
                continue
            if i < len(self.text)-len(svs) and self.text[i+len(svs)] != ' ':
                continue
                    
            if i != -1:
                # I found the slot value synonym from database in the 
                # sentence, I must replace it
                newSV = 'sv_'+sn
                self.valueDictCounter[newSV] += 1
                newSV = newSV+'-'+str(self.valueDictCounter[newSV])
                self.valueDict[newSV] = (sv, svs)
                
                self.text = self.replaceSV(self.text, newSV, svs, i)

                # find slot which match
                for slt in self.slots:      
                    if slt.name.endswith(sn) and slt.value == sv:
                        # I found matching slot, now I have to find slot 
                        # value in the sentence
                        slt.origValue = slt.value
                        slt.value = newSV
                        break                
                
        self.words = split(self.text)
        self.words = [self.vocabulary[w] for w in self.words]

    def genGrams(self):
        if self.settings == None:
            return
            
        self.grams = defaultdict(set)
        # generate unigrams, bigrams, and trigrams from text
        for i in range(len(self.words)):
            self.grams[(self.words[i],)].add((i,i+1))
        
        if self.settings['nGrams'] >=2:
            for i in range(1, len(self.words)):
                self.grams[(self.words[i-1],self.words[i])].add((i-1, i+1))
        if self.settings['nGrams'] >=3:
            for i in range(2, len(self.words)):
                self.grams[(self.words[i-2],self.words[i-1],self.words[i])].add((i-2,i+1))
        if self.settings['nGrams'] >=4:
            for i in range(3, len(self.words)):
                self.grams[(self.words[i-3],self.words[i-2],self.words[i-1],self.words[i])].add((i-3,i+1))

        if self.settings['nStarGrams'] >=3:
            for i in range(2, len(self.words)):
                self.grams[(self.words[i-2],'*1',self.words[i])].add((i-2, i+1))
        if self.settings['nStarGrams'] >=4:
            for i in range(3, len(self.words)):
                self.grams[(self.words[i-3],'*2',self.words[i])].add((i-3, i+1))
        if self.settings['nStarGrams'] >=5:
            for i in range(4, len(self.words)):
                self.grams[(self.words[i-4],'*3',self.words[i])].add((i-4, i+1))
        
    def render(self, speechAct, slots, origSV):
        DA = self.vocabulary.getKey(speechAct)
        rendered_slots = ','.join([each_slot.renderCUED(origSV,self.valueDict) for each_slot in slots])
        DA += '('+rendered_slots+')'

        return DA

    def renderCUED(self, origSV=False):
        return self.render(self.speechAct, self.slots, origSV)
        
    def renderTBED(self, origSV = True):
        return self.render(self.tbedSpeechAct, self.tbedSlots, origSV)

    def renderText(self):
        ws=[]
        for ew in self.words:
            if ew in self.valueDict:
                ws.append(self.valueDict[ew][1])
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
    
    def getErrors(self, dats, missingSlots, extraSlots):
        if self.speechAct != self.tbedSpeechAct:
            dats[self.speechAct].append(self)
            
        for each in self.slots-self.tbedSlots:
            missingSlots[each].append(self)
        for each in self.tbedSlots-self.slots:
            extraSlots[each].append(self)
        
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
        trans = set()
        
        # speech acts
        # return transformation for speech act only if the 
        # tbedSpeechAct is wrong
        if self.speechAct != self.tbedSpeechAct:
            trans.add(Transformation(speechAct=self.speechAct))
        
        # slot & values
        # return transformation for slot & value only if the 
        # the slot&value is missing or is it should not be here is wrong
        # self.tbedSlots array is list which we update (improve)
        missingSlotItems = self.getMissingSlotItems()
        extraSlotItems = self.getExtraSlotItems()
        
        for slot in missingSlotItems:
            trans.add(Transformation(addSlot=slot))
            
        for slot in extraSlotItems:
            trans.add(Transformation(delSlot=slot))

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
                        
                    trans.add(Transformation(subSlot=(es, ms, 'left')))
                    
                # allow to substitute the name
                if extraSlot.name != missingSlot.name:
                    es = deepcopy(extraSlot)
                    ms = deepcopy(missingSlot)
                    es.equal = None
                    es.value = None
                    ms.equal = None
                    ms.value = None
                        
                    trans.add(Transformation(subSlot=(es, ms, 'left')))
    
        # do not explode transformations, only one modification 
        # at one time is allowed
        
        return trans
        
    def genTriggers(self):
        # collect all posible triggers for all dimmensions 
        #   (speechAct, grams, slots)
        
        saCond = [None,]
        if self.settings['speechAct'] >=1:
            saCond.append(self.tbedSpeechAct)
        
        gramsCond = [None,]
        for gram1 in self.grams:
            gramsCond.append(gram1)
            
        slotsCond = [None,]
        if self.settings['nSlots'] >= 1:
            for slot in self.tbedSlots:
                slotsCond.append([deepcopy(slot),])
                
            if self.settings['nSlots'] >= 2:
                ts = list(self.tbedSlots)
                for i in range(len(ts)):
                    for j in range(i+1, len(ts)):
                        slotsCond.append([deepcopy(ts[i]),deepcopy(ts[j])])

        # sentece length rigger
        lengthCond = [None,]
        if self.settings['lngth'] >= 1:
            lengthCond.append(len(self.words))
        
        # sentece length rigger, None mean I do not care
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
            for gram in gramsCond:
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
