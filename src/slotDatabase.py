#!/usr/bin/env python2.5

from collections import *
from utils import *
import glob,re

class SlotDatabase:
    def __init__(self):
        self.db  = defaultdict(dset_factory)
##        self.db['near']['cinema'].add('cinema')
        self.values = []
        self.slotNamesValues  = defaultdict(list)
        
    def keys(self):
        return self.db.keys()
    
    def __getitem__(self, key):
        return self.db[key]
    
    def loadTAB(self, dir, removeDuplicates = True):
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

        for sn in self.db:
            for sv in self.db[sn]:
                for svs in self.db[sn][sv]:
                    self.slotNamesValues[sn].append((sv, svs, svs.count(' '), len(svs))) 
        for sn in self.slotNamesValues:
            self.slotNamesValues[sn].sort(cmp=lambda x,y: cmp(x[2], y[2]) if x[2] != y[2] else cmp(x[3], y[3]), reverse=True)
        
        if removeDuplicates:
            # I have to remove duplicates and create a new slot name for them
            # it will limit the degree of chaos for the process of db items replacement
            
            svsDict = defaultdict(list)
            for (sn, sv, svs, c, cc) in self.values:
                svsDict[svs].append((sn, sv))
            
            # all duplicit slot value synonyms has more than one (sn, sv) tuples
            for svs in svsDict:
                if len(svsDict[svs]) > 1:
                    # create a new slot name
                    newSN = '_x_'.join(sorted(set([x[0] for x in svsDict[svs]])))
                    # I have to have unique set of new slot values
                    newSVs = list(set([x[1] for x in svsDict[svs]]))
                    
                    if len(newSVs) == 1:
                        # I have only one slot value
                        # example:
                        # self.db['addr']['alexander hotel'] 
                        #       = ['alexander hotel', 'alexander', 'hotel']
                        # self.db['name']['alexander hotel'] 
                        #       = ['alexander hotel', 'alexander', 'hotel']
                        #
                        # the algoritmus will result in 
                        #
                        # self.db['addr_x_name']['alexander hotel'] 
                        #       = ['alexander hotel', 'alexander', 'hotel']
                        #
                        # because only the synonym 'hotel' is duplicit
                        
                        self.db[newSN][newSVs[0]].add(svs)
                    else:
                        # I can not have the same slot values 
                        # example:
                        # self.db['addr']['alexander hotel'] 
                        #       = ['alexander hotel', 'alexander', 'hotel']
                        # self.db['name']['primus hotel'] 
                        #       = ['primus hotel', 'primus', 'hotel']
                        #
                        # the algoritmus will result in 
                        #
                        # self.db['addr']['alexander hotel'] 
                        #       = ['alexander hotel', 'alexander']
                        # self.db['name']['primus hotel'] 
                        #       = ['primus hotel', 'primus']
                        pass
                        
                    # delete origonal duplicit svs
                    for (sn, sv) in svsDict[svs]:
                        self.db[sn][sv].remove(svs) 
            
            # regenerate the list of slot value synonyms
            self.values = []
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
        
            
    
