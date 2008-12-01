#!/usr/bin/env python2.5

from math import *
from copy import *

addSlotScoreWeight = 1.0 
delScoreWeight = 1.0
subScoreWeight = 2.0
# subScoreWeight = 0.5 # this works very well

class Transformation:
    # I implement only one modification at one time
    # If I allowed to performe more modifications than it would be 
    # to complex
    def __init__(self, speechAct = None, addSlot = None, delSlot = None, subSlot = None):
        self.speechAct = speechAct
        self.addSlot = addSlot
        self.delSlot = delSlot
        self.subSlot = subSlot
        self.occurence = 0
        
        return
        
    def __str__(self):
        s  = 'TRANS:'
        s += 'SpeechAct: %s - ' % str(self.speechAct)
        if self.addSlot != None:
            s += 'AddSlot: %s - ' % self.addSlot.renderCUED(False)
        else:
            s += 'AddSlot: None - '
            
        if self.delSlot != None:
            s += 'DelSlot: %s - ' % self.delSlot.renderCUED(False)
        else:
            s += 'DelSlot: None - '
            
        if self.subSlot != None:
            s += 'SubSlot: %s -' % str((self.subSlot[0].renderCUED(False), self.subSlot[1].renderCUED(False),self.subSlot[2]))
        else:
            s += 'SubSlot: None -'
        return s

    def __eq__(self, other):
        if self.speechAct == other.speechAct and self.addSlot == other.addSlot and self.delSlot == other.delSlot and self.subSlot == other.subSlot:
            return True
        
        return False
        
    def __hash__(self):
        h  = hash(self.speechAct)
        h += hash(self.addSlot)
        h += hash(self.delSlot)
        h += hash(self.subSlot)
        
        return h % (1 << 31) 
    
    def getOccurance(self):
        if self.subSlot != None:
            # substitution is prefered because it fix two error at once one 
            # deletion and one addition
            return self.occurence*2
        
        return self.occurence
        
    # measure only difference in performance
    # >0 - for corect modification
    #  0 - for no mofification
    # <0 - for wrong modification
    # I expect to perform only one modification at on time
    def measureDiff(self, da, trigger):
        """There is serious problem with evalating difference in performance of 
        operations deletion of .place="castle", I should differentiate between  
        deleting the slot if there is no "castle slot" in the reference and if 
        there is the "near="castle" slot. In the first case, I fixed three 
        errors: .place, =, and "castle". However, in the second case, it fixes
        only .place error but creates new erros: =, "castle" because it removes 
        the for the hypothesis.
        
        This I might be able to fix only in a new version which would 
        completely simulate tree editing.
        """
        
        netScore = 0.0
        posScore = 0.0
        negScore = 0.0

        if self.speechAct:
            if self.speechAct == da.speechAct:
                if self.speechAct != da.tbedSpeechAct:
                    netScore = 1
                    posScore = 1
                else:
                    netScore = 0
            else:
                if self.speechAct == da.tbedSpeechAct:
                    # this rule is not responsible for changing 
                    # dialogue act type to wrong dialogue act type because 
                    # the dialogue act type is already wrong
                    netScore = 0
                else:
                    netScore = -1
                    negScore = +1
                    
            return netScore*addSlotScoreWeight, posScore*addSlotScoreWeight, negScore*addSlotScoreWeight
                
        if self.addSlot:
            shouldbeIn = da.slots.count(self.addSlot)
            alreadyIn  = da.tbedSlots.count(self.addSlot)
            added      = len(trigger.getLexIndexes(da))
            needed     = shouldbeIn - alreadyIn
            
            if needed >= 0:
                if needed >= added:
                    # I reccieve points for all added slots up to needed number
                    netScore = added
                    posScore = added
                if needed < added:
                    # I want to add more slots than is needed. As a result, i 
                    # get points for all needed slots but I have to detract 
                    # points for all extra slots
                    netScore = needed - (added - needed)
                    posScore = netScore
            else:
                # there are already to many slots of this type and I still want 
                # to add more
                netScore = -added
                negScore = +added
            
            return netScore*addSlotScoreWeight, posScore*addSlotScoreWeight, negScore*addSlotScoreWeight
            
        if self.delSlot:
            # I can delete more than one slot. What I want to do is to delete 
            # a slot only when 

            # the trigger was validated globaly on the whole sentence,
            # now I have to validate the trigger localy
            lexIndexes = trigger.getLexIndexes(da)
                
            # now I should perform deletions only in proximity of lexIndexes
            deletable = [slot for slot in da.tbedSlots if self.delSlot.match(slot)]
            for slt in deletable:
                # I have matching tbedSlot
                # but is the lexical trigger in proximity of this slot? 
                
                for lexIndex in lexIndexes:
                    if slt.proximity(lexIndex, 'both'):
                        # the trigger is in proximity 'both' of the slot (slt)
                        
                        if slt in da.slots:
                            # transformation will introduce errors because this 
                            # slot is correct (it is in the reference slots) 
                            netScore -= 1
                            negScore += 1
                        else:
                            # in this case I really delete a slot which is not 
                            # in the reference semantics
                            netScore += 1 
                            posScore += 1
                            
            return netScore*delScoreWeight, posScore*delScoreWeight, negScore*delScoreWeight
            
##########################################################################
##########################################################################
            
        if self.subSlot:
            # the trigger was validated globaly on the whole sentence,
            # now I have to validate the trigger localy
            lexIndexes = trigger.getLexIndexes(da)
                
            # now I should perform substitution only in proximity of 
            # lexIndexes
            
            transformable = [slot for slot in da.tbedSlots if self.subSlot[0].match(slot)]
            for slt in transformable:
                # I have matching tbedSlot but is the 
                # lexical trigger in proximity of this slot? 
                for lexIndex in lexIndexes:
                    if slt.proximity(lexIndex, self.subSlot[2]):
                        # the trigger is in proximity of the slot (slt) as the 
                        # trigger expects (self.subSlot[2])
                        
                        if slt in da.slots:
                            # transformation will introduce errors because this 
                            # slot is correct (it is in the reference slots) 
                            netScore -= 1 # I break only one third
                            negScore += 1
                            continue
                            
                        s = deepcopy(slt)
                        self.subSlot[1].transform(s)
                        if s in da.slots:
                            # the tbed slot was transformed so that it is the 
                            # same as one of reference slots (da.slots)
                            netScore += 1 # I fix only one third
                            posScore += 1
                        else:
                            # I should not penalize for slots I could not fix, I 
                            # alreaddy penalized for those which are actualy 
                            # correct but they match subSlot[0]
                            netScore -= 0
            return netScore*subScoreWeight, posScore*subScoreWeight, negScore*subScoreWeight
                
        return 0
        
    def apply(self, da, trigger):
        # change the speech act
        if self.speechAct:
            if da.tbedSpeechAct != self.speechAct:
                da.tbedSpeechAct = self.speechAct
                return True
        
        applied = False
        
        # update slots
        if self.addSlot:
            lexIndexes = trigger.getLexIndexes(da)
##            print '>>>', da
##            print '---', trigger
##            print '+++', lexIndexes
            
            # add all triggered slots, I do not care from where they
            # come from, I just track what lexical items trigeered 
            # addition of these slots
            for each in lexIndexes:
                da.tbedSlots.append(deepcopy(self.addSlot))
                da.tbedSlots[-1].lexIndex.add(each[0])
                da.tbedSlots[-1].lexIndex.add(each[1])
            
            if len(lexIndexes) > 0:
                applied = True
                
            da.computeBorders()
            
        if self.delSlot:
            # I do not track deletion of slots
            
            # the trigger was validated globaly on the whole sentence,
            # now I have to validate the trigger localy
            lexIndexes = trigger.getLexIndexes(da)
            # now I should perform substitution only in proximity of 
            # lexIndexes
            deletable = [(i, slot) for (i, slot) in enumerate(da.tbedSlots) if self.delSlot.match(slot)]
            toDelete = set()
            for (i, slt) in deletable:
                # I have matching slot but is the lexical 
                # trigger in proximity of this slot?
                for lexIndex in lexIndexes:
                    if slt.proximity(lexIndex, 'both'):
                        # the trigger is in the proximity => delete slot
                        toDelete.add(i)
                        applied = True
            
            # keep only those slots which indexes are not in toDelete list
            da.tbedSlots = [slt for (i, slt) in enumerate(da.tbedSlots) if i not in toDelete]
                        
        if self.subSlot:
            # the trigger was validated globaly on the whole sentence,
            # now I have to validate the trigger localy
            lexIndexes = trigger.getLexIndexes(da)
            # now I should perform substitution only in proximity of 
            # lexIndexes
            transformable = [slot for slot in da.tbedSlots if self.subSlot[0].match(slot)]
            for slt in transformable:
                # I have matching slot but is the lexical 
                # trigger in proximity of this slot?
                for lexIndex in lexIndexes:
##                    print '---', da, 'lexI = ', lexIndex, 'slotI =', slt.leftBorder, slt.leftMiddle, slt.rightMiddle, slt.rightBorder
##                    print '---', slt, 'proximity =',slt.proximity(lexIndex)
                    if slt.proximity(lexIndex, self.subSlot[2]):
##                        print '>>>', slt, da
                        self.subSlot[1].transform(slt)
##                        print '<<<', slt
                        
                        # store indexes to the lexical realization of 
                        # the substituted (transformed) slot
                        slt.lexIndex.add(lexIndex[0])
                        slt.lexIndex.add(lexIndex[1])
                        
                        applied = True
        
        return applied
        
    def complexity(self):
        if self.speechAct:
            return 1
        if self.addSlot:
            return 1
        if self.delSlot:
            return 1
        if self.subSlot:
            return 1

        return 0
        
    @classmethod
    def read(cls, nTriggers):
        raise ValueError
        return cls()
        
    def write(self):
        s = ''
        
        if self.speechAct != None:
            s += 'Transformation:SpeechAct:'+str(self.speechAct)+'\n'
        if self.addSlot != None:
            s += 'Transformation:AddSlot:'+self.addSlot.renderCUED(False)+'\n'
        if self.delSlot != None:
            s += 'Transformation:DelSlot:'+self.delSlot.renderCUED(False)+'\n'
        if self.subSlot != None:
            s += 'Transformation:SubSlot: %s\n ' % str((self.subSlot[0].renderCUED(False), self.subSlot[1].renderCUED(False),self.subSlot[2]))
        return s
        
