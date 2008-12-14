#!/usr/bin/env python2.5

import re, pickle

from collections import *
from string import *

posDict = { 'arrive':   'VB', 
            'reach':    'VB', 
            'leave':    'VB', 
            'depart':   'VB', 
            'travel':   'VB', 
            'show':     'VB', 
            'connect':  'VB', 
            'return':	'VB',
            'from':     'IN', 
            'to':       'IN', 
            'at':       'IN', 
            'on':       'IN',
            'before':   'IN',
            'after':    'IN',
            'in':	'IN',
            'into':	'IN'
            }
            
lemmaDict= {'arrive':       'arrive',
            'arriving':     'arrive', 
            'arrives':      'arrive', 
            'arrived':      'arrive', 
            'reach':        'reach', 
            'reaching':     'reach', 
            'reaches':      'reach', 
            'reached':      'reach', 
            'leave':        'leave', 
            'leaving':      'leave', 
            'leaves':       'leave', 
            'left':         'leave', 
            'depart':       'depart', 
            'departing':    'depart', 
            'departs':      'depart', 
            'departed':     'depart', 
            'travel':       'travel', 
            'traveling':    'travel', 
            'travels':      'travel', 
            'traveled':     'travel', 
            'show':         'show',
            'showing':      'show',
            'shows':        'show',
            'showed':       'show',
            'connect':      'connect',
            'connecting':   'connect',
            'connects':     'connect',
            'connected':    'connect',
            'return':       'return',
            'returning':    'return',
            'returns':      'return',
            'returned':     'return',
            'stop':         'stop',
            'stoping':      'stop',
            'stops':        'stop',
            'stoped':       'stop',
            'from':         'from', 
            'to':           'to', 
            'at':           'at', 
            'on':           'on',
            'before':       'before',
            'after':        'after',
            'in':           'in',
            'into':         'into'
            }

def harmonicMean(x,y):
    try:
        return 2*x*y/(x+y)
    except ZeroDivisionError:
        return 0
    
def dset_factory():
    return defaultdict(set)

def dlist_factory():
    return defaultdict(list)

def powerset(s):
    result = set()

    l = len(s)
    for i in range(2**l):
        n = i
        x = []
        for j in range(l):
            if n & 1:
                x.append(s[j])
            n >>= 1
        if x:
            result.add(tuple(x))
    return result

def splitByComma(text):
    parentheses = 0
    splitList = []

    oldI=0
    for i in range(len(text)):
        if text[i] == '(':
            parentheses +=1
        elif text[i] == ')':
            parentheses -=1
            if parentheses < 0:
                raise ValueError("Missing a left parenthesis.") 
        elif text[i] == ',':
            if parentheses == 0:
                if oldI == i:
                    raise ValueError("Splited segmend do not have to start with a comma.") 
                else:
                    splitList.append(text[oldI:i].strip())
                    oldI = i+1
    else:
        splitList.append(text[oldI:].strip())

    return splitList

def splitTAB(text):
    parentheses = 0
    splitList = []

    oldI=0
    swith = True
    for i in range(len(text)):
        if swith and text[i] == '"':
            parentheses +=1
            swith = False
        elif not swith and text[i] == '"':
            parentheses -=1
            swith = True
            if parentheses < 0:
                raise ValueError("Missing a left \".") 
        elif text[i] in ('\t', ' '):
            if parentheses == 0:
                if oldI == i:
                    print text
                    print i, '"',text[i],'"'
                    raise ValueError("Splited segmend do not have to start with a separator.") 
                else:
                    splitList.append(text[oldI:i].strip())
                    oldI = i+1
    else:
        splitList.append(text[oldI:].strip())

    return splitList
    
##class adict(dict):
##    def __init__(self, invisible=True):
##        dict.__init__(self)
##        self.iter = 0
##        self.rev = {}
##        self.invisible = invisible
##        
##    def __getitem__(self, key):
##        try:
##            return dict.__getitem__(self, key)
##        except KeyError:
##            self.iter += 1
##            
##            if self.invisible:
##                dict.__setitem__(self, key, key)
##                self.rev[key] = key
##                return key
##            else:
##                dict.__setitem__(self, key, self.iter)
##                self.rev[self.iter] = key
##                return self.iter
##                        
##    def getKey(self, value):
##        try:
##            return self.rev[value]
##        except KeyError:
##            raise ValueError('Wrong dict value.')
##            
##    def write(self, fn):
##        f = file(fn, 'wb')
##        pickle.dump(self, f)
##        f.close()
##        return
##    
##    @classmethod
##    def read(cls, fn):
##        f = file(fn, 'rb')
##        c = pickle.load(f)
##        f.close()
##        return c
