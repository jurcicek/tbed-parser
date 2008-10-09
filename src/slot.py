#!/usr/bin/env python2.5

from string import *
import re
from operator import *

from utils import *

class Slot:
    def __init__(self, cuedSlot):
        self.cuedSlot = cuedSlot
        
        # train data values
        self.name=''
        self.value=''
        self.equal=''
        
        return

    def parse(self):
        self.equal = True
        i = self.cuedSlot.find('!=')
        if i == -1:
          i = self.cuedSlot.find('=')
          if i == -1:
              self.name = self.cuedSlot
              
              return
        else:
            self.equal = False

        self.name = self.cuedSlot[:i]

        self.value = self.cuedSlot[i:]
        self.value = self.value.replace('!', '')
        self.value = self.value.replace('=', '')
        self.value = self.value.replace('"', '')

        return
        
    def renderCUED(self):
        name = self.name
            
        if self.equal:
            equal = '='
        else:
            equal = '!='
        
        if not self.value:
            value = ''
            equal = ''
        else:
            value = self.value

        return name+equal+value
