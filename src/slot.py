#!/usr/bin/env python2.5

import re
from string import *
from operator import *

from utils import *

slot_value_search = 0
slot_value_extra = 0

class Slot:
    def __init__(self, cuedSlot):
        self.cuedSlot = cuedSlot
        
        # train data values
        self.name = None
        self.equal = None
        self.value = None
        self.lexIndex = set()
        
        self.leftBorder = None
        self.leftMiddle = None
        self.rightMiddle = None
        self.rightBorder = None

    def __str__(self):
        raise ValueError('Program must decide whether thios slot is CUED or TBED.')

    def __eq__(self, other):
        if not isinstance(other, Slot):
            return False
            
        if  self.name == other.name and self.equal == other.equal and self.value == other.value:
            return True
        
        return False
        
    def __hash__(self):
        h  = hash(self.name)
        h += hash(self.equal)
        h += hash(self.value)
        
        return h % (1 << 31) 

    def match(self, other):
        '''
        This method returns True if the targed 'other' slot has 
        equal attributes for attributes defined by this slot.
        '''
        if self.name != None:
            if self.name != other.name:
                return False
            
        if self.equal != None:    
            if self.equal != other.equal:
                return False
        
        if self.value != None:
            if self.value != other.value:
                return False
                
        return True
    
    def transform(self, other):
        ''' 
        This method modifies atributes of 'other' slot if this 
        slot defines them.
        '''
        
        if self.name != None:
            other.name = self.name
            
        if self.equal != None:    
            other.equal = self.equal
        
        if self.value != None:
            other.value = self.value
    
    def proximity(self, lexIndex, type):
        prx = 'none'
        if self.leftBorder <= lexIndex[0] and lexIndex[1] <= self.rightBorder:
            prx = 'both'
        if self.leftBorder <= lexIndex[0] and lexIndex[1] <= self.rightMiddle:
            prx = 'left'
        if self.leftMiddle <= lexIndex[0] and lexIndex[1] <= self.rightBorder:
            prx = 'right'
        if self.leftMiddle <= lexIndex[0] and lexIndex[1] <= self.rightMiddle:
            prx = 'centre'

        if type == 'left':
            if prx == 'left' or prx == 'centre':
                return True
        elif type == 'right':
            if prx == 'right' or prx == 'centre':
                return True
        elif type == 'both':
            if prx == 'both' or prx == 'right' or prx == 'left' or prx == 'centre':
                return True
                
        return False
        
    def parse(self):
        i = self.cuedSlot.find('!=')
        if i == -1:
            i = self.cuedSlot.find('=')
            if i == -1:
              self.name = self.cuedSlot
              self.equal = ''
              self.value = ''
              return
            else:
                self.equal = '='
        else:
            self.equal = '!='

        self.name = self.cuedSlot[:i]

        self.value = self.cuedSlot[i:]
        self.value = self.value.replace('!', '')
        self.value = self.value.replace('=', '')
        self.value = self.value.replace('"', '')
        
        if self.value == 'value':
            raise ValueError('FIX: Francois has in the training data slot items with values "value". These slots should be ignored!')
        if self.value == 'pm':
            raise ValueError('FIX: Francois has in the training data slot items with values "pm". These slots should be ignored!')
        
    def renderCUED(self, origSV):
        if self.name != None:
            name = self.name
        else:
            name = '*'
            
        if self.equal != None:
            equal = self.equal
        else:
            equal = '*='
        
        if self.value != None:
            if origSV and hasattr(self, 'origValue'):
                value = self.origValue
            else:
                value = self.value
                
            if value:
                value = '"'+value+'"'
        else:
            value = '*'
            
##        return name+equal+value+'|'+str(self.lexIndex)+'|'
        return name+equal+value

    def renderTBED(self, origSV, valueDictPositions, words):
        global slot_value_search, slot_value_extra
        
        if self.name != None:
            name = self.name
        else:
            name = '*'
            
        if self.equal != None:
            equal = self.equal
        else:
            equal = '*='
        
        if self.value != None:
            if origSV and self.value.startswith('sv_'):
                value = 'not_recovered_slot_value'
                # I have to find the original value for the slot value
                match = []
                for i in range(self.leftBorder, self.rightBorder+1):
##                for i in range(self.leftMiddle, self.rightMiddle+1):
                    # find the positon of the slot value in the sentence
                    if self.value == words[i]:
                        # I found the position of teh slot value, now I have to recover 
                        # the original value
                        match.append(i)

                slot_value_search += 1
                slot_value_extra += len(match) - 1 
                
                if len(match) > 2:
                    print name, equal, self.value, self.lexIndex, words
                
                    for i in range(self.leftBorder, self.rightBorder+1):
##                    for i in range(self.leftMiddle, self.rightMiddle+1):
                        print words[i]
                        
                    print 'Slot value search: %d Slot values extra: %d' % (slot_value_search,slot_value_extra)
                
                value = valueDictPositions[match[-1]][0]
            else:
                value = self.value
                
            if value:
                value = '"'+value+'"'
        else:
            value = '*'
            
##        return name+equal+value+'|'+str(self.lexIndex)+'|'
        return name+equal+value
