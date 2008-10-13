#!/usr/bin/env python2.5

from string import *
import re
from copy import *

from utils import *
from slot import *
from transformation import *
      
class DialogueAct:
    def __init__(self, cuedDA, text):
        # train data values
        self.text = text
        self.cuedDA = cuedDA

        self.speechAct = ''
        self.slots = []
        
        # tbed data
        self.tbedSpeechAct = 'inform'
        self.tbedSlots = []
        
        # temporal tbed data, for rules evaluation
        self.tmpTbedSpeechAct = 'inform'
        self.tmpTbedSlots = []
        
        return

    def __str__(self):
        s = self.text+' - '
        s+= self.cuedDA+' - '
        s+= self.speechAct+' - '
        s+= self.tbedSpeechAct+' - '
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
    
    def resetTmp(self):
        self.tmpTbedSpeechAct = self.tbedSpeechAct
        self.tmpTbedSlots = copy(self.tbedSlots)
    
    def parse(self):
        self.words = split(self.text)
        numOfDAs = len(splitByComma(self.cuedDA))
        if numOfDAs > 1:
            raise ValueError('Too many DAs in input text.')

        # get the speech-act
        i = self.cuedDA.index("(")
        self.speechAct = self.cuedDA[:i]
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
            self.slots.append(each_slot)

        return

    def genGrams(self,nGrams):
        self.grams = set()
        if len(self.grams) == 0:
            # generate unigrams, bigrams, and trigrams from text
            for i in range(len(self.words)):
                self.grams.add((self.words[i],))
            
            try:
                if nGrams >=2:
                    for i in range(1, len(self.words)):
                        self.grams.add((self.words[i-1],self.words[i]))

                if nGrams >=3:
                    for i in range(2, len(self.words)):
                        self.grams.add((self.words[i-2],self.words[i-1],self.words[i]))
            except IndexError:
                pass
    
    def render(self, speechAct, slots):
        DA = speechAct
        rendered_slots = ""
        
        if len(slots) > 0:
            rendered_slots = ""

            for each_slot in slots:
##                rendered_slots += each_slot.renderCUED() + ','
                rendered_slots += each_slot + ','

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
        
    def measure(self, tmp=False):
        # get similarity measure
        if tmp:
            if self.tmpTbedSpeechAct == self.speechAct:
                Ha = 1
            else:
                Ha = 0
                
            Na = 1
            
            # slots measures
            Hi = len(set(self.tmpTbedSlots)&set(self.slots))
            Ri = len(self.tmpTbedSlots)
            Ni = len(self.slots)
            
            return (Ha, Na, Hi, Ri, Ni)
        else:
            if self.tbedSpeechAct == self.speechAct:
                Ha = 1
            else:
                Ha = 0
                
            Na = 1
            
            # slots measures
            Hi = len(set(self.tbedSlots)&set(self.slots))
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
#        missingSlotAndValues = set(self.slots) - set(self.tbedSlots)
#        extraSlotAndValues = set(self.tbedSlots) - set(self.slots)
        
#        for slot in missingSlotAndValues:
#            trans.add(Transformation(addSlot=slot))
            
#        for slot in extraSlotAndValues:
#            trans.add(Transformation(delSlot=slot))
        
        # do not forget explode transformations
        # it would be to time consuming -> I am skiping it
        
        return trans
        
    def genTriggers(self, tplGrams):
        # collect all posible triggers for all dimmensions 
        #   (speachAct, grams, slots)
        
        saCond = [None, self.tbedSpeechAct]
        
        gramsCond = [None,]
        for gram1 in self.grams:
            gramsCond.append([gram1,])
            
            if tplGrams >= 2:
                for gram2 in self.grams:
                    if gram1 != gram2:
                        gramsCond.append([gram1,gram2])


        slotsCond = [None,]
#        for slot in self.tbedSlots:
#            slotsCond.append([slot,])
                        
        # generate triggers
        triggers = set()
        # explode trigger combinations
        for sa in saCond:
            for gram in gramsCond:
                for slot in slotsCond:
                    triggers.add(Trigger(speechAct=sa, grams=gram, slots = slot))
        
        return triggers

        
