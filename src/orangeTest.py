#!/usr/bin/env python2.5

import orange, orngStat, orngTree, orngC45, orngEnsemble

trainData  = '../data/towninfo-train.sem.o.txt'

#trainData  = '../data/towninfo-dev.sem.o.txt'

devData    = '../data/towninfo-dev.sem.o.txt'
testData   = '../data/towninfo-test.sem.o.txt'

##trainData  = '../data/towninfo-train.asr.o.txt'
##devData    = '../data/towninfo-dev.asr.o.txt'
##testData   = '../data/towninfo-test.asr.o.txt'

# Description: An implementation of bagging (only bagging class is defined here)
# Category:    modelling
# Referenced:  c_bagging.htm

import orange, random

def BLearner(examples=None, **kwds):
    learner = apply(BLearner_Class, (), kwds)
    if examples:
        return learner(examples)
    else:
        return learner

class BLearner_Class:
    def __init__(self, learner, t=10, name='bagged classifier'):
        self.t = t
        self.name = name
        self.learner = learner

    def __call__(self, examples, weight=None):
        r = random.Random()
        r.seed(0)

        n = len(examples)
        classifiers = []
        for i in range(self.t):
            selection = []
            for j in range(n):
                selection.append(r.randrange(n))
            data = examples.getitems(selection)
            classifiers.append(self.learner(data))
            
        return BClassifier(classifiers = classifiers, name=self.name, domain=examples.domain)

class BClassifier:
    def __init__(self, **kwds):
        self.__dict__ = kwds

    def __call__(self, example, resultType = orange.GetValue):
        freq = [0.] * len(self.domain.classVar.values)
        for c in self.classifiers:
            freq[int(c(example))] += 1
        index = freq.index(max(freq))
        value = orange.Value(self.domain.classVar, index)
        for i in range(len(freq)):
            freq[i] = freq[i]/len(self.classifiers)
        if resultType == orange.GetValue: return value
        elif resultType == orange.GetProbabilities: return freq
        else: return (value, freq)
        

def showBranch(node, classvar, lev, i, f):
    var = node.tested
    if node.nodeType == 1:
        f.write("\n"+"|   "*lev + "%s = %s:" % (var.name, var.values[i]))
        printTree0(node.branch[i], classvar, lev+1,f)
    elif node.nodeType == 2:
        f.write("\n"+"|   "*lev + "%s %s %.1f:" % (var.name, ["<=", ">"][i], node.cut))
        printTree0(node.branch[i], classvar, lev+1,f)
    else:
        inset = filter(lambda a:a[1]==i, enumerate(node.mapping))
        inset = [var.values[j[0]] for j in inset]
        if len(inset)==1:
            f.write("\n"+"|   "*lev + "%s = %s:" % (var.name, inset[0]))
        else:
            f.write("\n"+"|   "*lev + "%s in {%s}:" % (var.name, ", ".join(inset)))
        printTree0(node.branch[i], classvar, lev+1,f)

def printTree0(node, classvar, lev, f):
    var = node.tested
    if node.nodeType == 0:
        f.write("%s (%.1f)" % (classvar.values[int(node.leaf)], node.items))
    else:
        for i, branch in enumerate(node.branch):
            if not branch.nodeType:
                showBranch(node, classvar, lev, i, f)
        for i, branch in enumerate(node.branch):
            if branch.nodeType:
                showBranch(node, classvar, lev, i, f)

def dumpC45Tree(tree, f):
    printTree0(tree.tree, tree.classVar, 0, f)
    
def accuracy(test_data, classifiers):
    correct = [0.0]*len(classifiers)
    for ex in test_data:
        for i in range(len(classifiers)):
            if classifiers[i](ex) == ex.getclass():
                correct[i] += 1
    for i in range(len(correct)):
        correct[i] = 100.0*correct[i] / len(test_data)
        
    return correct

# set up the classifiers
trainD = orange.ExampleTable(trainData)
devD = orange.ExampleTable(devData)
testD = orange.ExampleTable(testData)

majority = orange.MajorityLearner(trainD)
majority.name   = 'majority         '
print majority.name

##tree = orngTree.TreeLearner(trainD, measure='gainRatio', binarization=0, minSubset=5, minExamples=5, sameMajorityPruning=1, mForPruning=5);
##tree.name       = "tree - gainRatio "
##f = file(trainData+'o.txt.tree', 'w')
##f.write(orngTree.dumpTree(tree, leafStr='%V (%^.2m% = %.0M out of %.0N)'))
##f.close()
##print tree.name

##treeC45 = orange.C45Learner(trainD, minObjs=5)
##treeC45.name    = "tree - C45       "
##f = file(trainData+'o.txt.C45tree', 'w')
##dumpC45Tree(treeC45,f)
##f.close()
##print treeC45.name

t = orngTree.TreeLearner(measure='gainRatio', binarization=0, minSubset=2, minExamples=2, sameMajorityPruning=1, mForPruning=2);
bsTree = BLearner(learner=t, examples=trainD)
bsTree.name     = "bsTree           "
print bsTree.name

c45 = orange.C45Learner(minObjs=2)
bsC45 = BLearner(learner=c45, examples=trainD)
bsC45.name      = "bsC45            "
print bsC45.name

##svm = orange.SVMLearner(trainD)
##svm.name      = "SVM              "

##classifiers = [majority, tree, bsTree, treeC45, bsC45]
classifiers = [majority, bsTree, bsC45]

# compute accuracies
print '='*80
acc = accuracy(trainD, classifiers)
print "Classification accuracies - train:"
print '-'*80
for i in range(len(classifiers)):
    print classifiers[i].name, acc[i]

print '='*80
# compute accuracies
acc = accuracy(devD, classifiers)
print "Classification accuracies - dev:"
print '-'*80
for i in range(len(classifiers)):
    print classifiers[i].name, acc[i]

print '='*80
# compute accuracies
acc = accuracy(testD, classifiers)
print "Classification accuracies - test:"
print '-'*80
for i in range(len(classifiers)):
    print classifiers[i].name, acc[i]
