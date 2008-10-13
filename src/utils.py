#!/usr/bin/env python2.5

from string import *
import re, pickle

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

class adict(dict):
    def __init__(self, invisible=True):
        dict.__init__(self)
        self.iter = 0
        self.rev = {}
        self.invisible = invisible
        
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            self.iter += 1
            
            if self.invisible:
                dict.__setitem__(self, key, key)
                self.rev[key] = key
                return key
            else:
                dict.__setitem__(self, key, self.iter)
                self.rev[self.iter] = key
                return self.iter
                        
    def getKey(self, value):
        try:
            return self.rev[value]
        except KeyError:
            raise ValueError('Wrong dict value.')
            
    def write(self, fn):
        f = file(fn, 'wb')
        pickle.dump(self, f)
        f.close()
        return
    
    @classmethod
    def read(cls, fn):
        f = file(fn, 'rb')
        c = pickle.load(f)
        f.close()
        return c
