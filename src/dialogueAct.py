#!/usr/bin/env python2.5

from string import *
import re
from copy import *
from collections import *

from utils import *
from slot import *
from transformation import *
from trigger import *
      
class DialogueAct:
    def __init__(self, cuedDA, text, vocabulary):
        # train data values
        self.cuedDA = cuedDA
        self.text = text
        self.vocabulary = vocabulary

        self.speechAct = self.vocabulary['']
        self.slots = set()
        
        # tbed data
        self.tbedSpeechAct = self.vocabulary['inform']
        self.tbedSlots = set()
        
        return

    def __str__(self):
        s = self.text+' - '
        s+= self.cuedDA+' - '
        s+= self.vocabulary.getKey(self.speechAct)+' - '
        s+= self.vocabulary.getKey(self.tbedSpeechAct)+' - '
        s+= str(self.slots)+' - '
        s+= str(self.tbedSlots)+' - '
        s+= str(self.grams)

        return s
        
    def __copy__(self):
        cDA = DialogueAct(self.cuedDA, self.text)
        cDA.speechAct = self.speechAct
        cDA.tbedSpeechAct = self.tbedSpeechAct
        cDA.slots = self.slots
        cDA.tbedSlots = copy(self.tbedSlots)
        
        cDA.words = self.words
        cDA.grams = self.grams
        
        return cDA
    
    def parse(self):
        self.words = split(self.text)
        self.words = [self.vocabulary[w] for w in self.words]
        
        numOfDAs = len(splitByComma(self.cuedDA))
        if numOfDAs > 1:
            raise ValueError('Too many DAs in input text.')

        # get the speech-act
        i = self.cuedDA.index("(")
        self.speechAct = self.vocabulary[self.cuedDA[:i]]
        slots = self.cuedDA[i:]
        slots = slots.replace('(', '')
        slots = slots.replace(')', '')

        if slots == '':
            # no slots to process
            return
            
        # split slots
        slots = splitByComma(slots)
        
        for each_slot in slots:
##            slot = Slot(each_slot)
##            slot.parse()
            self.slots.add(self.vocabulary[each_slot])

        return

    def genGrams(self, trgCond):
        self.grams = set()
        # generate unigrams, bigrams, and trigrams from text
        for i in range(len(self.words)):
            self.grams.add((self.words[i],))
        
        if trgCond['nGrams'] >=2:
            for i in range(1, len(self.words)):
                self.grams.add((self.words[i-1],self.words[i]))
        if trgCond['nGrams'] >=3:
            for i in range(2, len(self.words)):
                self.grams.add((self.words[i-2],self.words[i-1],self.words[i]))
        if trgCond['nGrams'] >=4:
            for i in range(3, len(self.words)):
                self.grams.add((self.words[i-3],self.words[i-2],self.words[i-1],self.words[i]))

        if trgCond['nStarGrams'] >=3:
            for i in range(2, len(self.words)):
                self.grams.add((self.words[i-2],'*',self.words[i]))
        if trgCond['nStarGrams'] >=4:
            for i in range(3, len(self.words)):
                self.grams.add((self.words[i-3],'*','*',self.words[i]))
        if trgCond['nStarGrams'] >=5:
            for i in range(4, len(self.words)):
                self.grams.add((self.words[i-4],'*','*','*',self.words[i]))
            
                    
    def render(self, speechAct, slots):
        DA = self.vocabulary.getKey(speechAct)
        rendered_slots = ""
        
        if len(slots) > 0:
            rendered_slots = ""

            for each_slot in slots:
##                rendered_slots += each_slot.renderCUED() + ','
                rendered_slots += self.vocabulary.getKey(each_slot) + ','

            # remove the last comma
            rendered_slots = re.sub(r',$', '', rendered_slots)

        DA += '('+rendered_slots+')'

        return DA

    def renderCUED(self):
        return self.render(self.speechAct, self.slots)
        
    def renderTBED(self):
        return self.render(self.tbedSpeechAct, self.tbedSlots)
        
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
        # self.tbedSlots array is actually list we update (improve)
        missingSlotAndValues = self.slots-self.tbedSlots
        extraSlotAndValues = self.tbedSlots-self.slots
        
        for slot in missingSlotAndValues:
            trans.add(Transformation(addSlot=slot))
            
        for slot in extraSlotAndValues:
            trans.add(Transformation(delSlot=slot))
        
        # do not explode transformations, only one modification 
        # at one time is allowed
        
        return trans
        
    def genTriggers(self, trgCond):
        # collect all posible triggers for all dimmensions 
        #   (speechAct, grams, slots)
        
        saCond = [None,]
        if trgCond['speechAct'] >=1:
            saCond.append(self.tbedSpeechAct)
        
        tplFilter = defaultdict(int)
        gramsCond = [None,]
        for gram1 in self.grams:
            gramsCond.append([gram1,])
            
            if trgCond['tplGrams'] >= 2:
                for gram2 in self.grams:
                    if gram1 != gram2 and tplFilter[(gram2,gram1)]!=1:
                        gramsCond.append([gram1,gram2])
                        tplFilter[(gram1,gram2)] = 1

        slotsCond = [None,]
        if trgCond['nSlots'] >= 1:
            for slot in self.tbedSlots:
                slotsCond.append([slot,])

        # sentece length rigger
        lengthCond = [None,]
        if trgCond['lngth'] >= 1:
            lengthCond.append(len(self.words))
        
        # generate triggers
        triggers = set()
        # explode trigger combinations
        for sa in saCond:
            for gram in gramsCond:
                for slot in slotsCond:
                    for lngth in lengthCond:
                        triggers.add(Trigger(speechAct=sa, 
                                                grams=gram, 
                                                slots=slot,
                                                lngth=lngth))
        
        return triggers
