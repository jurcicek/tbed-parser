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
        
##        self.leftBorder = None
##        self.rightBorder = None

    def __str__(self):
        return self.renderCUED()

    def __eq__(self, other):
        if not isinstance(other, Slot):
            return False
            
        if  self.name == other.name and self.equal == other.equal and self.value == other.value and self.lexIndex == other.lexIndex:
            return True
        
        return False
        
    def __hash__(self):
        h  = hash(self.name)
        h += hash(self.equal)
        h += hash(self.value)
        
        for each in self.lexIndex:
            h += hash(each)
            
        return h % (1 << 31) 

    def validate(self, other):
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
        self.value = '"'+self.value.replace('"', '')+'"'
        self.value = self.value.replace('""', '')
        
    def renderCUED(self):
        if self.name != None:
            name = self.name
        else:
            name = '?:'
            
        if self.equal != None:
            equal = self.equal
        else:
            equal = '=?='
            
        if self.value != None:
            value = self.value
        else:
            value = '"?"'
            
        return name+equal+value
