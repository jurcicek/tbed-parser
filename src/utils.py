#!/usr/bin/env python2.5

import re, pickle

from collections import *
from string import *

def separateApostrophes(text):
    text = text.replace("'ll ", " 'll ")
    text = text.replace("'re ", " 're ")
    text = text.replace("'ve ", " 've ")
    text = text.replace("'m ", " 'm ")
    text = text.replace("'d ", " 'd ")
    text = text.replace("'s ", " 's ")
    text = text.replace("n't", " n't")
    text = text.replace("/ ", " / ")
    
    return text
    
def replaceSV(text, sn, sv, i):
    return text[0:i]+sn+text[i+len(sv):]
    
def prepareForRASP(text, db, capitalize = True):
    valueDictCounter = defaultdict(int)
    valueDict = {}
    p = False
        
    for (sn, sv, svs, c, cc) in db.values:
        i = 0
        while True:
            # we must search several times for the SVS value
            i = text.find(svs,i)
            if i != -1:
                # test wheather there are spaces around the word. that it is not a 
                # substring of another word!
                if i > 0 and text[i-1] != ' ':
                    i += 1
                    continue
                    
                if i < len(text)-len(svs) and text[i+len(svs)] != ' ':
                    i += 1
                    continue
                    
                # I found the slot value synonym from database in the 
                # sentence, I must replace it
                newSV1 = 'sv_'+sn
                valueDictCounter[newSV1] += 1
                newSV2 = newSV1+'-'+str(valueDictCounter[newSV1])
                valueDict[newSV2] = (sv, svs)
                
                text = replaceSV(text, newSV2, svs, i)

            else:
                break

    words = text.split()
    
    if capitalize:
        for i, w in enumerate(words):
            if w.startswith('sv_'):
                w = w.lower()
                
                if w.find('_name') != -1 or w.find('manufacturer') != -1:
                    words[i] = '-'.join(valueDict[w][1].title().split())
                elif w.find('_code') != -1:
                    words[i] = '-'.join(valueDict[w][1].upper().split())
                else:
                    words[i] = '-'.join(valueDict[w][1].split())
                    
        words[0] = words[0][0].upper()+words[0][1:]
    else:
        # I do not want to capitalize slot values,
        # I just want them to compact into one term by using '-'
        for i, w in enumerate(words):
            if w.startswith('sv_'):
                if w.find('_name') != -1 or w.find('manufacturer') != -1:
                    words[i] = '-'.join(valueDict[w][1].split())
                elif w.find('_code') != -1:
                    words[i] = '-'.join(valueDict[w][1].split())
                else:
                    words[i] = '-'.join(valueDict[w][1].split())
    
    text = ' '.join(words)+' .'
    
    # fix some capitalization
    if capitalize:
        text = text.replace(" i ", " I ")
    
    return text
            
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
