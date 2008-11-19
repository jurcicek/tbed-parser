#!/usr/bin/env python2.5

from collections import *
from utils import *
import glob,re

class SlotDatabase:
    def __init__(self):
        self.db  = defaultdict(dset_factory)
##        self.db['near']['cinema'].add('cinema')
        self.values = []
        
    def keys(self):
        return self.db.keys()
    
    def __getitem__(self, key):
        return self.db[key]
    
    def loadTAB(self, dir):
        for fn in glob.glob(dir+'/*.tab'):
            f = file(fn, 'r')
            
            for l in f.readlines():
                l = l.strip()
                if not l:
                    continue
                l = re.sub('\s+', ' ', l)
                l = splitTAB(l)
                # normalize text strings, only one space character
                l = [' '.join(x.replace('"', '').split()) for x in l if x] 
                
                if len(l) >= 2:
                    synonyms = set()
                    
                    exp = tuple(l[0].split(' '))
                    synonyms.add(exp)
                    # add synonyms (if there are any)
                    for i in range(2, len(l)):
                        exp = tuple(l[i].split(' '))
                        synonyms.add(exp)
                    
##                    extSynonyms = set()
##                    for syn in synonyms:
##                        extSynonyms.update(powerset(syn))
##                    
                    extSynonyms = synonyms
                    extSynonyms = set([' '.join(x) for x in extSynonyms])

                
                    # add all value for the slot name
                    if extSynonyms:
                        self.db[l[1]][l[0]].update(extSynonyms)
                        
            f.close()
        
        for sn in self.db:
            for sv in self.db[sn]:
                for svs in self.db[sn][sv]:
                    self.values.append((sn, sv, svs, svs.count(' '), len(svs))) 
        
        self.values.sort(cmp=lambda x,y: cmp(x[3], y[3]) if x[3] != y[3] else cmp(x[4], y[4]), reverse=True)

##        print self.values
##        print self.db['city_name']['tampa']
##        print self.db['city_name']['new york']
##        print self.db['city_name']['miami']
        
    def isNameInDB(self, name):
        """Add better matching for slot names."""
        return self.db.has_key(name)
        
    def getSlotNameValueSynonyms(name, value):
        """I might add better matching between slot name and name.
        for example fromloc.city_name ?= city_name.
        """ 
        return self.db[name][value]
        
            
    
