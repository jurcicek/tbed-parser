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
    def __init__(self, fos, fosa):
        BaseTD.__init__(self, fos = fos, fosa = fosa)
        
        return
        
    def decode(self):
        i = 0
        for rule in self.bestRules:
            Ha = Na = Hi = Ri = Ni = 0
            for da in self.das:
                rule.apply(da)
                pHa, pNa, pHi, pRi, pNi = da.measure()
                
                Ha += pHa
                Na += pNa
                Hi += pHi
                Ri += pRi
                Ni += pNi
            
            try:
                acc  = 100.0*Ha/Na
            except ZeroDivisionError:
                acc  = 0.0

            try:
                prec = 100.0*Hi/Ri
                rec  = 100.0*Hi/Ni
                f = 2*prec*rec/(prec+rec)
                af = 2*acc*f/(acc+f)
            except ZeroDivisionError:
                prec = 0.0
                rec  = 0.0
                f    = 0.0
                af   = acc

            i += 1
            print 'Rule:%d' % i
            print '%s AF: %.2f ACC: %.2f F:%.2f PREC: %.2f REC: %.2f' %(rule, af, acc, f, prec, rec)
                
        return
    
    def writeOutput(self, fn):
        f = file(fn, 'w')
        
        for da in self.das:
            f.write('%s <=> %s\n' % (da.text, da.renderTBED()))
            
        return
        
