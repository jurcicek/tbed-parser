#!/usr/bin/env python2.5

from collections import *
import glob

def dset_factory():
    return defaultdict(set)
    
class SlotDatabase:
    def __init__(self):
        self.db  = defaultdict(dset_factory)
##        self.db['near']['cinema'].add('cinema')

    def keys(self):
        return self.db.keys()
    
    def __getitem__(self, key):
        return self.db[key]
        
    def loadTAB(self, dir):
        for fn in glob.glob(dir+'/*.tab'):
            f = file(fn, 'r')
            
            for l in f.readlines():
                l = l.strip().replace('"', '').split('\t')
                
                # add all value for the slot name
                self.db[l[1]][l[0]].add(l[0])
                # add synonyms (if there aare any)
                for i in range(2, len(l)):
                    self.db[l[1]][l[0]].add(l[i])

            f.close()
        
        return
    
    def isNameInDB(self, name):
        """Add better matching for slot names."""
        return self.db.has_key(name)
        
    def getSlotNameValueSynonyms(name, value):
        """I might add better matching between slot name and name.
        for example fromloc.city_name ?= city_name.
        """ 
        return self.db[name][value]
        
            
    
