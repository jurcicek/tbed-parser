#!/usr/bin/env python2.5

import re
from string import *
from copy import *
from collections import *

from utils import *
from slot import *
from transformation import *
from trigger import *
      
class DialogueAct:
    def __init__(self, cuedDA, origSentence, raspData, db, settings):
        # train data values
        self.cuedDA = cuedDA
        self.db = db
        self.settings = settings
        self.origText = origSentence
        
        self.normText = origSentence
        self.normText = prepareForRASP(origSentence, self.db, False)
        self.normText = separateApostrophes(self.normText)
        self.raspText = self.normText
        
        if self.settings['useDeps'] == 0:
            self.lemmas = self.getLemmas(self.normText)
            self.posTags = self.getPOSTags(self.normText)
        else:
            # separate deps and text
            raspSenetence, raspDeps = raspData.strip().split('|||')
            
            # separate text, lemmas, and POS tags, deps
            self.raspText = self.getText(raspSenetence)
            self.lemmas = self.getLemmas(raspSenetence)
            self.posTags = self.getPOSTags(raspSenetence)
            self.deps = self.getDeps(raspDeps)
          
        # print problematic input
        # both normalized text and text from RASP should have the same number
        # of terms
        if len(self.normText.split(' ')) != len(self.raspText.split(' ')):
            print 'Warning:'
            print len(self.normText.split(' ')), self.normText
            print len(self.raspText.split(' ')), self.raspText
            print
        
        self.speechAct = ''
        self.slots = []
        
        self.tbedSpeechAct = ''
        self.tbedSlots = []
        
        self.valueDictCounter = defaultdict(int)
        self.valueDict = {}
        
        # in this array I store all rules applied on the DA in 
        # the sequencial order
        self.ruleTracker = []

    def __str__(self):
        s = self.text+' - '
        s+= self.cuedDA+' - '
        s+= self.speechAct+' - '
        s+= self.tbedSpeechAct+' - '
        s+= str(self.slots)+' - '
        s+= str(self.tbedSlots)+' - '

        return s

    def computeBorders(self):
        '''
        This method compute borders for each slot in this dialogue act. 
        Borders of each slot definy proximity 'atrea' where the lexical 
        triggers must be triggered so that SubSlot operation chould be
        applied on particular slot.
        
        FIX: Some slot might dominate the same words; as a result, they shoud have
        the same borders. It is not implemented now.
        '''
        for each in self.tbedSlots:
            if not each.lexIndex:
                raise ValueError('Slot has lexical alignment set.')
                
            each.leftMiddle = min(each.lexIndex)
            each.rightMiddle = max(each.lexIndex)
            
        self.tbedSlots.sort(cmp=lambda x, y: cmp(x.leftMiddle, y.leftMiddle))
        
        if len(self.tbedSlots) > 0:
            self.tbedSlots[0].leftBorder = 0
            for i in range(1, len(self.tbedSlots)):
                self.tbedSlots[i].leftBorder = self.tbedSlots[i-1].rightMiddle+1
            
            for i in range(0, len(self.tbedSlots)-1):
                self.tbedSlots[i].rightBorder = self.tbedSlots[i+1].leftMiddle-1
                    
            self.tbedSlots[-1].rightBorder = len(self.words)-1
            
            for i in range(len(self.tbedSlots)):
                if self.tbedSlots[i].leftBorder > self.tbedSlots[i].leftMiddle:
                    self.tbedSlots[i].leftBorder = self.tbedSlots[i].leftMiddle
                if self.tbedSlots[i].rightBorder < self.tbedSlots[i].rightMiddle:
                    self.tbedSlots[i].rightBorder = self.tbedSlots[i].rightMiddle
            
##        print '+'*80
##        print self.text
##        for each in self.tbedSlots:
##            print each.renderCUED(), each.leftBorder, each.leftMiddle, each.rightMiddle, each.rightBorder

    def writeAlignment(self, f):
        f.write('.'*80+'\n')
        f.write(' '.join(['%s'  % w for w in self.words])+'\n')
        f.write(' '.join(['%*d' % (len(w), i) for i, w in enumerate(self.words)])+'\n')
            
        for each in self.tbedSlots:
            numberOfLeftDots = sum([len(w)+1 for i, w in enumerate(self.words) if i < each.leftBorder])
            numberOfLeftDashes = sum([len(w)+1 for i, w in enumerate(self.words) if i >= each.leftBorder and i<each.leftMiddle])
            numberOfEquals = sum([len(w)+1 for i, w in enumerate(self.words) if i >= each.leftMiddle and i<=each.rightMiddle])
            numberOfRightDashes = sum([len(w)+1 for i, w in enumerate(self.words) if i > each.rightMiddle and i<=each.rightBorder])
            numberOfRightDots = sum([len(w)+1 for i, w in enumerate(self.words) if i > each.rightBorder])
            f.write(' '*numberOfLeftDots)
            f.write('-'*numberOfLeftDashes)
            f.write('='*numberOfEquals)
            f.write('-'*numberOfRightDashes)
            f.write(' '*numberOfRightDots+'\n')
            
            f.write('%50s (%.2d,%.2d,%.2d,%.2d) <= %s\n' % (each.renderTBED(False, self.valueDictPositions, self.words), each.leftBorder, each.leftMiddle, each.rightMiddle, each.rightBorder, str(sorted(each.lexIndex))))
        f.write('.'*80+'\n')

    def getPOSTags(self, text):
        t = text.split()
        p = re.compile(r'.*_')
        pos = [p.sub('', x) for x in t]
        
        self.allPOSTags = set(pos)
        
        if '.' in self.allPOSTags: 
            self.allPOSTags.remove('.')
        
        return pos

    def getLemmas(self, text):
        t = text.split()
        p = re.compile(r'(\+\w+|):\d+_\S+$')
        pos = [p.sub('', x) for x in t]

        return pos
        
    def getText(self, text):
        t = text.split()
        p = re.compile(r':\d+_\S+$')
        t = [p.sub('', x) for x in t]
        
        pos = ' '.join(t)
        
        return pos
        
    def getDeps(self, deps):
        """ This method process dependencies from RASP 2.0.
        The method create and return a dictionary which contains for each 
        position in the self.words (and also self.lemmas, self.POSTags) dependecy 
        link to another position(s). Each link contains: type if link (obj, 
        ncsubj, ...) a
        """
        
        if not deps:
            return dict()
            
##        print '='*80
##        print self.normText
##        print self.raspText
##        print self.lemmas
        deps = deps[1:-1].replace('|', '').split(')(')
##        print deps
        
        # remove POS tags
        p = re.compile(r'_[$2&a-z]+')
        deps = [p.sub('', x) for x in deps]
##        print deps
        
        depsDict = {}
        for d in deps:
            d = d.split()
            d = [x for i, x in enumerate(d) if i == 0 or x.find(':') != -1]
            
            if len(d) != 3:
                # ignore all non direct (simple) dependecies
                continue
            
            d[1] = d[1].split(':')
            d[1][1] = int(d[1][1]) - 1
            d[2] = d[2].split(':')
            d[2][1] = int(d[2][1]) - 1

            if len(d) != 3:
                print '*'*3, d
                
            # build the links, from leaves to roots, index is position in the 
            # sentence
            
            # build only tree, do not allow overwriting
            # how ever control what is kept in the tree
            if d[2][1] in depsDict:
                # ignore ncsubj dependecy, e.g.:
                # hi i need to get a flight from memphis to salt-lake-city 
                #  depart+ing before 10am .
                # --- ['dobj', ['to', 9], ['salt-lake-city', 10]]
                # +++ ['ncsubj', ['depart+ing', 11], ['salt-lake-city', 10]]
                # 
                if d[0] == 'ncsubj':
                    continue
                    
                # 'dobj' dependecy is more interesting
                if depsDict[d[2][1]][0] == 'dobj' and d[0] == 'obj':
                    continue
                    
##                print '#'*1000
##                print '-'*3, rd[d[2][1]]
##                print '+'*3, d

                depsDict[d[2][1]] = d
            else:
                # no colision addit freely
                depsDict[d[2][1]] = d
            
##        print rd

        return depsDict

    def parse(self):
        cuedDA = self.cuedDA
        
        numOfDAs = len(splitByComma(cuedDA))
        if numOfDAs > 1:
            raise ValueError('Too many DAs in input text.')

        # get the speech-act
        i = cuedDA.index("(")
        speechAct = cuedDA[:i]
        slots = cuedDA[i:].lower()
        slots = slots.replace('(', '')
        slots = slots.replace(')', '')
        
        slts = []
        if slots == '':
            # no slots to process
            slots = []
        else:
            # split slots
            slots = splitByComma(slots)
            for slt in slots:
                try:
                    s = Slot(slt)
                    s.parse()
                    slts.append(s)
                except ValueError:
                    # check for invalid slot items
                    pass

        self.speechAct = speechAct
        self.slots = slts

    def replaceSV(self, text, sn, sv, i):
        return text[0:i]+sn+text[i+len(sv):]
        
    def replaceDBItems(self):
        """
        This method replace all lexical ralizations of database items
        by some tags in form 'sv_slotname-N', where N is counter of occurence in 
        the sentence. There is a problem if some slot value occures in different 
        slots (names). Than only one association is made correctly. 
        
        There is also another issue with db items. Some words are replaced 
        although they are not db items. For example a word 'one' is replaced by 
        'sv-stars-1' in sentence 'I would like this one', which is apparently 
        wrong.
        """

        if self.settings == None:
            return
            
        if self.settings['DBItems'] != 'replace':
            return
        
##        f = file('dbItemsReplacement.txt', 'a')
##        f.write('#'*80+'\n')
##        f.write('Text:         '+ self.normText+'\n')
        
        for (sn, sv, svs, c, cc) in self.db.values:
            i = 0
            while True:
                i = self.normText.find(svs,i)
                if i != -1:
                    # test wheather there are spaces around the word. that it is not a 
                    # substring of another word!
                    if i > 0 and self.normText[i-1] != ' ':
                        i += 1
                        continue
                    if i < len(self.normText)-len(svs) and self.normText[i+len(svs)] != ' ':
                        i += 1
                        continue
                            
                    # I found the slot value synonym from database in the 
                    # sentence, I must replace it
                    newSV1 = 'sv_'+sn
                    self.valueDictCounter[newSV1] += 1
                    newSV2 = newSV1+'-'+str(self.valueDictCounter[newSV1])
                    self.valueDict[newSV2] = (sv, svs)
                    
                    self.normText = self.replaceSV(self.normText, newSV2, svs, i)

                    # find slot which match
                    for slt in self.slots:      
                        # I do not check wheter there is the same name of the slot name
                        # for the substituted  slot value. If I chose a wrong slot
                        # value label, I have to learn how to fix it
                        
##                        if slt.value == "new york":
##                            print slt.value
##                            print  sn, sv, self.db[sn][sv]

                        if slt.value in self.db[sn][sv]:
                            slt.origValue = slt.value
                            slt.value = newSV2
                            break
                else:
                    break

        self.words = split(self.normText)
        
        # now I have to get rid of indexes and create dictionary
        # with positions and correct slot values
        
        self.valueDictPositions = {}
        for i, w in enumerate(self.words):
            if w.startswith('sv_'):
                self.valueDictPositions[i] = self.valueDict[w]

        self.words = split(self.normText)

        sv_count = {}
        sv_map = {}
        for p in sorted(self.valueDictPositions):
            sv_count[self.words[p][:-2]] = 0
        for p in sorted(self.valueDictPositions):
            sv_map[self.words[p]] = self.words[p][:-2]+'-'+str(sv_count[self.words[p][:-2]] % 2)
            sv_count[self.words[p][:-2]] += 1
            
##        print '-'*80
##        print self.text
####        print sv_count
##        print sv_map
####        print
##        
##        for p in sorted(self.valueDictPositions):
##            print p, self.words[p], sv_map[self.words[p]], self.valueDictPositions[p]
        
        # update self.words
        for i, w in enumerate(self.words): 
            if w.startswith('sv_'):
                self.words[i] = sv_map[w]
        # as a result, I have to update text        
        self.normText = ' '.join(self.words)
        
        # update slot values
        for slt in self.slots:      
            if slt.value in sv_map:
                slt.value = sv_map[slt.value]
        
##        for k, v in sorted(self.valueDictPositions.items()):
##            f.write('Subst value:  %2d => %30s = %s\n' % (k, v, self.words[k]))
##        f.write('DB Text:      '+ self.normText+'\n')
##        f.write('Slots:        '+ str([x.renderCUED(False) for x in self.slots]))
##        f.write('\n')
##        f.close()

##        print '#', self.lemmas
        # replace DB items in lemmas
        
        try:
            for i in range(len(self.lemmas)):
                if self.words[i].startswith('sv_'):
                    self.lemmas[i] = self.words[i]
        except IndexError, ei:
            print self.origText
            print self.normText
            print self.raspText
            print self.words
            print self.lemmas
            
            raise ei
            
##        print '-', self.words
##        print '+', self.lemmas

    def genGrams(self, gramIDF):
        if not hasattr(self, 'settings'):
            return
        
        if not hasattr(self, 'word'):
            # I did not run replaceDBItems(); as a result, I have to split text
            self.words = split(self.normText)
        
        self.grams = defaultdict(set)
        # generate regular unigrams, bigrams, trigrams, ... from text
        
        for i in range(len(self.words)):
            self.grams[(self.words[i],)].add((i,i))
        
        if self.settings['nGrams'] >=2:
            for i in range(1, len(self.words)):
                self.grams[(self.words[i-1],self.words[i])].add((i-1, i))
        if self.settings['nGrams'] >=3:
            for i in range(2, len(self.words)):
                self.grams[(self.words[i-2],self.words[i-1],self.words[i])].add((i-2,i))
        if self.settings['nGrams'] >=4:
            for i in range(3, len(self.words)):
                self.grams[(self.words[i-3],self.words[i-2],self.words[i-1],self.words[i])].add((i-3,i))

        # generate skiping (I call it star) bigrams
        if self.settings['nStarGrams'] >=3:
            for i in range(2, len(self.words)):
                self.grams[(self.words[i-2],'*1',self.words[i])].add((i-2, i))
        if self.settings['nStarGrams'] >=4:
            for i in range(3, len(self.words)):
                self.grams[(self.words[i-3],'*2',self.words[i])].add((i-3, i))
        if self.settings['nStarGrams'] >=5:
            for i in range(4, len(self.words)):
                self.grams[(self.words[i-4],'*3',self.words[i])].add((i-4, i))
                
        # generate nearest left POS tag lemma bigrams
        if self.settings['useDeps'] and self.settings['nearestLeftPOSWord']:
            for i, w in enumerate(self.words):
                # generate long ranging dependencies only for slot values
                if w.startswith('sv_'):
                    # generate LRD for all pos tags, the learning alg. will 
                    # chose all suitable POS resp. triggers
                    for pos in self.allPOSTags:
                        # find nearest left POS tag
                        for j in range(i-1, -1, -1):
                            if self.posTags[j] == pos:
                                # I got the nearest left POS tag
##                                if j < i-1:
##                                    print w
##                                    print pos
##                                    print j, i
##                                    print self.origText
##                                    print self.normText
##                                    print self.words[j]
##                                    print self.lemmas[j]
##                                    print self.posTags[j]
##                                    print (self.lemmas[j],'*nl-'+pos,w)
##                                    print len(self.words), self.words
##                                    print len(self.lemmas),self.lemmas
##                                    print len(self.posTags),self.posTags
##                                    print '='*80
                                
                                # I am interested only in non slot values
                                if not self.lemmas[j].startswith('sv_'):
                                    self.grams[(self.lemmas[j],'*nl-'+pos,w)].add((i, i))
                                    
                                # do not search for any POS pos word any more
                                break

        # generate nearest dep tree POS tag lemma bigrams
        if self.settings['useDeps'] and self.settings['nearestDepTreePOSWord']:
            for i, w in enumerate(self.words):
                # generate long ranging dependencies only for slot values
                if w.startswith('sv_'):
                    # generate LRD for all pos tags, the learning alg. will 
                    # chose all suitable POS resp. triggers
                    for pos in self.allPOSTags:
##                        print '='*80
##                        print self.allPOSTags
##                        print self.normText
##                        print self.posTags
##                        print self.lemmas[i]
##                        print '-'*80
                        j = self.nearestDepTreePosWord(i, pos)
                        if j != -1:
                            self.grams[(self.lemmas[j],'*nt-'+pos,w)].add((i, i))
##                            print '+++',(self.lemmas[j],'*nt-'+pos,w)
                            
        # delete all 'dot' grams, they are useless
        grms = self.grams.keys()
        for g in grms:
            if '.' in g:
                del self.grams[g]
        
        for g in self.grams:
            gramIDF[g] += 1.0

    def nearestDepTreePosWord(self, i, pos, r = 0):
        r += 1
        if r > 10:
            return -1
            
        try:
            j = self.deps[i][1][1] 
##            print pos, self.posTags[j], self.deps[i]
        except KeyError:
            # pos wos not found
            return -1
            
        if self.posTags[j] == pos:
##            print j, self.lemmas[j]
            if self.lemmas[j].startswith('sv_'):
                # I am interested only in non slot values
                return -1
            else:
                return j
        else:
            return self.nearestDepTreePosWord(j, pos, r)
        
    def removeGrams(self, remGrams):
        """ I prune all grams from the list remGrams. Only singleton grams across 
        all dialogue acts should be removed. The method returns all deleted grams.
        
        Once deleted gram does not have to be tested again becasue we know that was 
        a singleton across all DAs.
        """
        
        ret = []
        for rg in remGrams:
            if rg in self.grams:
                del self.grams[rg]
                ret.append(rg)
                
        return ret
            
    def renderCUED(self, origSV=False):
        DA = self.speechAct
        rendered_slots = ','.join([each_slot.renderCUED(origSV) for each_slot in self.slots])
        DA += '('+rendered_slots+')'

        return DA
        
    def renderTBED(self, origSV = True):
        DA = self.tbedSpeechAct
        rendered_slots = [each_slot.renderTBED(origSV, self.valueDictPositions,self.words) for each_slot in self.tbedSlots]
        
        # I filter out sequencial duplicities among slot
        # in other words on the output of the parser cannot be two same slots behind each 
        # other => must be true: slts[i] != slts[i+1]
        rendered_slots_filtered = []
        if len(rendered_slots) > 0:
            rendered_slots_filtered.append(rendered_slots[0])
            for slt in rendered_slots[1:]:
                if slt != rendered_slots_filtered[-1]:
                    rendered_slots_filtered.append(slt)
                
        DA += '('+','.join(rendered_slots_filtered)+')'
        
        return DA

    def renderText(self):
        if self.settings['useDeps'] == 0:
            ws=[]
            for i, ew in enumerate(self.words):
                if i in self.valueDictPositions:
                    ws.append(self.valueDictPositions[i][1])
                else:
                    ws.append(ew)
            return ' '.join(ws)
        else:
            return self.origText
            
    def getNumOfSlots(self):
        return len(self.slots)
        
    def measure(self):
        # get similarity measure
        if self.tbedSpeechAct == self.speechAct:
            Ha = 1
        else:
            Ha = 0
            
        Na = 1
        
        # slots measures
        Hi = len(self.tbedSlots&self.slots)
        Ri = len(self.tbedSlots)
        Ni = len(self.slots)
            
        return (Ha, Na, Hi, Ri, Ni)

    def incorrectTbed(self):
        if self.speechAct != self.tbedSpeechAct or self.slots != self.tbedSlots:
            return True
        
        return False
    
    def getErrors(self, dats, missingSlots, extraSlots, substitutedSlots):
        if self.speechAct != self.tbedSpeechAct:
            dats[self.speechAct].append(self)
            
        for each in self.getMissingSlotItems():
            missingSlots[each].append(self)
        for each in self.getExtraSlotItems():
            extraSlots[each].append(self)
        
        for mi in self.getMissingSlotItems():
            for ei in self.getExtraSlotItems():
                if mi.value == ei.value:
                    substitutedSlots[mi][ei].append(self)
                    
        return
    
    def getMissingSlotItems(self):
        msi = []
        for si in self.slots:
            if si not in self.tbedSlots:
                msi.append(si)
        return msi
    
    def getExtraSlotItems(self):
        esi = []
        for si in self.tbedSlots:
            if si not in self.slots:
                esi.append(si)
        return esi
        
    def genTrans(self):
        # return a set of all posible modifications of the current DA
        # I use the dictionary to measure how many times the transformation
        # can be potentinaly usevul for this DA. Most of teh time the value 
        # will be equal zero but of DAs it might be different. 
        # If I estimate occurences properly. I can sort rules more preciselly.
        trans = defaultdict(int)
        
        # speech acts
        # return transformation for speech act only if the 
        # tbedSpeechAct is wrong
        if self.speechAct != self.tbedSpeechAct:
            trans[Transformation(speechAct=self.speechAct)] += 1
        
        # slot & values
        # return transformation for slot & value only if the 
        # the slot&value is missing or is it should not be here is wrong
        # self.tbedSlots array is list which we update (improve)
        missingSlotItems = self.getMissingSlotItems()
        extraSlotItems = self.getExtraSlotItems()
        
        for slot in missingSlotItems:
            trans[Transformation(addSlot=slot)] += 1 
            
        for slot in extraSlotItems:
            trans[Transformation(delSlot=slot)] += 1 

        for extraSlot in extraSlotItems:
            for missingSlot in missingSlotItems:
                # allow to substitute the equal sign
##                if extraSlot.equal != missingSlot.equal and extraSlot.value == missingSlot.value:
                if extraSlot.equal != missingSlot.equal:
                    es = deepcopy(extraSlot)
                    ms = deepcopy(missingSlot)
                    es.name  = None
                    es.value = None
                    ms.name  = None
                    ms.value = None
                        
                    trans[Transformation(subSlot=(es, ms, 'left'))] += 1 
                    
                # allow to substitute the name
                if extraSlot.name != missingSlot.name:
                    es = deepcopy(extraSlot)
                    ms = deepcopy(missingSlot)
                    es.equal = None
                    es.value = None
                    ms.equal = None
                    ms.value = None
                        
                    trans[Transformation(subSlot=(es, ms, 'left'))] += 1 
        
        for t in trans:
            t.occurence += trans[t]
            
        # do not explode transformations, only one modification 
        # at one time is allowed
        
        return set(trans.keys())
        
    def genTriggers(self):
        # collect all posible triggers for all dimmensions 
        #   (speechAct, grams, slots)
        # a gram must be always part of the trigger
        
        saCond = [None,]
        if self.settings['speechAct'] >=1:
            saCond.append(self.tbedSpeechAct)
        
        slotsCond = [None,]
        if self.settings['nSlots'] >= 1:
            for slot in self.tbedSlots:
                slotsCond.append([deepcopy(slot),])
                
        # sentece hasSlot trigger, None mean I do not care
        hasSlotsCond = [None,]
        if self.settings['hasSlots'] >= 1:
            if len(self.tbedSlots) == 0:
                hasSlotsCond.append(1) # False
            else:
                hasSlotsCond.append(2) # True
            
        # generate triggers
        triggers = set()
        # explode trigger combinations
        for sa in saCond:
            for gram in self.grams:
                for slot in slotsCond:
                    for hasSlots in hasSlotsCond:
                        triggers.add(
                            Trigger(speechAct=sa, 
                                    gram=gram, 
                                    slots=slot,
                                    hasSlots=hasSlots))
        
        return triggers
