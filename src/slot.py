#!/usr/bin/env python2.5

import re
from string import *
from operator import *

from utils import *

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
        return self.renderCUED(False, None)

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
    
    def proximity(self, lexIndex):
        if self.leftBorder <= lexIndex[0] and lexIndex[1] <= self.rightMiddle:
            return 'left'
        if self.leftMiddle <= lexIndex[0] and lexIndex[1] <= self.rightBorder:
            return 'right'
        if self.leftBorder <= lexIndex[0] and lexIndex[1] <= self.rightBorder:
            return 'both'

        return 'none'
        
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
        
    def renderCUED(self, origSV, valueDict):
        if self.name != None:
            name = self.name
        else:
            name = '*'
            
        if self.equal != None:
            equal = self.equal
        else:
            equal = '*='
        
        if self.value != None:
            if origSV and self.value in valueDict:
                value = valueDict[self.value][0]
            else:
                value = self.value
                
            if value:
                value = '"'+value+'"'
        else:
            value = '*'
            
##        return name+equal+value+'|'+str(self.lexIndex)+'|'
        return name+equal+value
