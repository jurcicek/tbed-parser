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

        return s

    def parseDA(self, cuedDA, text):
        words = split(text)
        words = [self.vocabulary[w] for w in words]
        
        numOfDAs = len(splitByComma(cuedDA))
        if numOfDAs > 1:
            raise ValueError('Too many DAs in input text.')

        # get the speech-act
        i = cuedDA.index("(")
        speechAct = self.vocabulary[cuedDA[:i]]
        slots = cuedDA[i:].lower()
        slots = slots.replace('(', '')
        slots = slots.replace(')', '')
        
        if slots == '':
            # no slots to process
            slots = set()
        else:
            # Francois hack:
            slots = slots.replace('.!=', '!=').replace('zeroProb-','')
            
            # split slots
            slots = splitByComma(slots)
            # unify slot values with Francois, scoring this modification should 
            # accept without any problems
            for i in range(len(slots)):
                j = slots[i].find('=')
                if j !=-1:
                    slots[i] = slots[i].replace('=', '="')+'"'
                    slots[i] = slots[i].replace('""', '"')
                    
            slots = set([self.vocabulary[si] for si in slots])
        
        return words, speechAct, slots

    def parse(self):
        self.words, self.speechAct, self.slots = self.parseDA(self.cuedDA, self.text)
       
        return
    
    def parseTbed(self, cuedDA, text):
        if text != self.text:
            raise ValueError('Loaded tbed text must equal to the training text.')
            
        self.words, self.tbedSpeechAct, self.tbedSlots = self.parseDA(cuedDA, text)
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

        for extraSlot in extraSlotAndValues:
            for missingSlot in missingSlotAndValues:
                trans.add(Transformation(subSlot=(extraSlot, missingSlot)))
    
        # do not explode transformations, only one modification 
        # at one time is allowed
        
        return trans
        
    def genTriggers(self, trgCond):
        # collect all posible triggers for all dimmensions 
        #   (speechAct, grams, slots)
        
        saCond = [None,]
        if trgCond['speechAct'] >=1:
            saCond.append(self.tbedSpeechAct)
        
        gramsCond = [None,]
        for gram1 in self.grams:
            gramsCond.append([gram1,])
            
        slotsCond = [None,]
        if trgCond['nSlots'] >= 1:
            for slot in self.tbedSlots:
                slotsCond.append([slot,])
                
            if trgCond['nSlots'] >= 2:
                ts = list(self.tbedSlots)
                for i in range(len(ts)):
                    for j in range(i+1, len(ts)):
                        slotsCond.append([ts[i],ts[j]])

        # sentece length rigger
        lengthCond = [None,]
        if trgCond['lngth'] >= 1:
            lengthCond.append(len(self.words))
        
        # sentece length rigger, None mean I do not care
        hasSlotsCond = [None,]
        if trgCond['hasSlots'] >= 1:
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
                                        grams=gram, 
                                        slots=slot,
                                        lngth=lngth,
                                        hasSlots=hasSlots))
        
        return triggers
