#!/usr/bin/env python2.5

from string import *
import re
from copy import *

from utils import *
from slot import *
from dialogueAct import *
from rule import *

from baseTD import *

class Decoder(BaseTD):
    def __init__(self, fos, fosa, trgCond):
        BaseTD.__init__(self, fos=fos, fosa=fosa, trgCond=trgCond)
        
        return
        
    def decode(self, verbose = False):
        for rule in self.bestRules:
            for da in self.das:
                rule.apply(da)
                
        return
    
    def writeOutput(self, fn):
        f = file(fn, 'w')
        
        for da in self.das:
            f.write('%s <=> %s\n' % (da.text, da.renderTBED()))
            
        return
