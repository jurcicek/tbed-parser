#!/usr/bin/env python2.5

from math import *
from copy import *

slotScoreNorm = 1.0 

class Transformation:
    # I implement only one modification at one time
    # If I allowed to performe more modifications than it would be 
    # to complex
    def __init__(self, speechAct = None, addSlot = None, delSlot = None, subSlot = None):
        self.speechAct = speechAct
        self.addSlot = addSlot
        self.delSlot = delSlot
        self.subSlot = subSlot
        
        return
        
    def __str__(self):
        s  = 'TRANS:'
        s += 'SpeechAct: %s - ' % str(self.speechAct)
        s += 'AddSlot: %s - ' % str(self.addSlot)
        s += 'DelSlot: %s - ' % str(self.delSlot)
        if self.subSlot != None:
            s += 'SubSlot: %s -' % str([str(x) for x in self.subSlot])
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
        if self.speechAct:
            ret = 0
            if self.speechAct == da.speechAct:
                if self.speechAct != da.tbedSpeechAct:
                    ret = 1
                else:
                    ret = 0
            else:
                if self.speechAct == da.tbedSpeechAct:
                    # this rule is not responsible for changing 
                    # dialogue act type to wrong dialogue act type because 
                    # the dialogue act type is already wrong
                    ret = 0
                else:
                    ret = -1
                    
            return ret/slotScoreNorm
                
        if self.addSlot:
            shouldbeIn = da.slots.count(self.addSlot)
            alreadyIn  = da.tbedSlots.count(self.addSlot)
            added      = len(trigger.getLexIndexes(da))
            needed     = shouldbeIn - alreadyIn
            
            ret = 0
            if needed >= 0:
                if needed >= added:
                    # I reccieve points for all added slots up to needed number
                    ret = added
                if needed < added:
                    # I want to add more slots than is needed. As a result, i 
                    # get points for all needed slots but I have to dtract 
                    # points for all extra slots
                    ret = needed - (added - needed)
            else:
                # there are already to many slots of this type and I still want 
                # to add more
                ret = -added
            
            return ret/slotScoreNorm
            
        if self.delSlot:
            shouldbeIn = da.slots.count(self.delSlot)
            alreadyIn  = da.tbedSlots.count(self.delSlot)
            deleted    = len(trigger.getLexIndexes(da))
            if alreadyIn < deleted:
                # I cannot delete slots which are not in tbedSlots
                # at maximum I can delete alreadyIn slots 
                deleted = alreadyIn
            notNeeded   = alreadyIn - shouldbeIn

            ret  = 0
            if notNeeded >= 0:
                if notNeeded >= deleted:
                    # I reccieve points for all deleted slots up to not needed 
                    # number
                    ret = deleted
                if notNeeded < deleted:
                    # I want to delete more slots than is not needed. As a 
                    # result, I get points for all needed slots but I have to 
                    # detract points for all missing slots
                    ret = notNeeded - (deleted - notNeeded)
            else:
                # there are missing slots of this type and I still want 
                # to delete some
                ret = -deleted
            
            return ret/slotScoreNorm
            
        if self.subSlot:
            ## I can correct or damage more than one slot
            ## I have to correct computation of benefits of the rule
        
            # the trigger was validated globaly on the whole sentence,
            # now I have to validate the trigger localy
            lexIndexes = trigger.getLexIndexes(da)
                
            # now I should perform substitution only in proximity of 
            # lexIndexes
            
            ret = 0
            transformable = [slot for slot in da.tbedSlots if self.subSlot[0].match(slot)]
            for slt in transformable:
                # I have matching tbedSlot which is not in slots but is the 
                # lexical trigger in proximity of this slot? If it is not triggered by gram than it is always in proximity
                for lexIndex in lexIndexes:
                    if slt.proximity(lexIndex) == self.subSlot[2]:
                        # the trigger is in proximity of the slot (slt) as the 
                        # trigger expects (self.subSlot[2])
                        
                        if slt in da.slots:
                            # transformation will introduce errors because this 
                            # slot is correct (it is in the reference slots) 
                            ret -= 1 # I break only one third
                            continue
                            
                        s = deepcopy(slt)
                        self.subSlot[1].transform(s)
                        if s in da.slots:
                            # the tbed slot was transformed so that it is the 
                            # same as one of reference slots (da.slots)
                            ret += 1 # I fix only one third
                        else:
                            # I should not penalize for slots I could not fix, I 
                            # alreaddy penalized for those which are actualy 
                            # correct but they match subSlot[0]
                            ret -= 0
            return ret*2
                
        return 0
        
    def apply(self, da, trigger):
        # change the speech act
        if self.speechAct:
            da.tbedSpeechAct = self.speechAct
            return
        
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
                
            da.computeBorders()
            
        if self.delSlot:
            # I do not track deletion of slots
            for slt in da.tbedSlots:
                if self.delSlot.match(slt):
                    da.tbedSlots.remove(slt)

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
                    if slt.proximity(lexIndex) == self.subSlot[2]:
##                        print '>>>', slt, da
                        self.subSlot[1].transform(slt)
##                        print '<<<', slt
                        
                        # store indexes to the lexical realization of 
                        # the substituted (transformed) slot
                        slt.lexIndex.add(lexIndex[0])
                        slt.lexIndex.add(lexIndex[1])
        
        return
        
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
            s += 'Transformation:AddSlot:'+str(self.addSlot)+'\n'
        if self.delSlot != None:
            s += 'Transformation:DelSlot:'+str(self.delSlot)+'\n'
        if self.subSlot != None:
            s += 'Transformation:SubSlot: %s\n ' % str([str(x) for x in self.subSlot])
        return s
        
