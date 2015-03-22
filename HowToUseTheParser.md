This section describe the basic usage of the TBL parser.

# Requirements #

To run our scripts, you will need working
  * Linux environment, Python (minimum v 2.5),
  * [SciPy](http://www.scipy.org/) is needed for its NumPy.
  * [matplotlib](http://matplotlib.sourceforge.net/) is needed for its plotting capabilities.
  * [The RASP System](http://www.informatics.susx.ac.uk/research/groups/nlp/rasp/) is needed for its POS tagging and dependency parsing capabilities. If you are not interested in long-range features than you do not need RASP.

# Installation #

Checkout the project into your home directory. The name of the directory for the TBL parser should be `tbed-parser`. If you want to have read/write access to the project SVN tree use the following command (you also have to be a contributor in this project)
```
svn checkout http://tbed-parser.googlecode.com/svn/trunk/ tbed-parser --username YOUR-USER-NAME
```
or
```
svn checkout http://tbed-parser.googlecode.com/svn/trunk/ tbed-parser
```
the read-only version.

Then add the **"~/tbed-parser/bin"** directory into your PATH.

# Run an example #

Go to the  "~/tbed-parser/" directory:
```
cd ~/tbed-parser
```

Run command from the bash command line:
```
./train ./experiment/debug
```
Consequently, in the directory "results", a new directory with results of the experiment will be created. The directory will be named as "YEAR-MONTH-DAY-HOUR-MINUTE" and its content will be similar to the following listing:
```
debug-dev.sem.hyp       debug-test.sem.hyp       debug-train.sem.hyp       debug-train.sem.pckl-bestrules  rules.txt
debug-dev.sem.hyp.algn  debug-test.sem.hyp.algn  debug-train.sem.hyp.algn  debug-train.sem.pckl-decoder    settings
debug-dev.sem.hyp.anlz  debug-test.sem.hyp.anlz  debug-train.sem.hyp.anlz  debug-train.sem.rules
debug-dev.sem.hyp.rslt  debug-test.sem.hyp.rslt  debug-train.sem.hyp.rslt  rules.pckl-bestrules
debug-dev.sem.hyp.stat  debug-test.sem.hyp.stat  debug-train.sem.hyp.stat  rules.pckl-decoder
```

Once you are in this directory, you can use commands like `grph-atis` and `grph-towninfo`.  The purpose of this commands is to plot the F-measure of the TBL parser for different number of used rules on the training, development and test data. Note that these commands are for the ATIS and TownInfo datasets. You have to modify the scripts to work with the debug dataset or your dataset.

# Results #

The file **rules.txt** contains learned rules. For example:
```
-------------------------------------------------------------
Rule:0:Occ:0:Net:2
Transformation:SpeechAct:inform
-------------------------------------------------------------
Rule:1:Occ:12:Net:9
Trigger:Gram:('sv_drinks-0',)
Transformation:AddSlot:drinks="sv_drinks-0"
-------------------------------------------------------------
Rule:2:Occ:6:Net:4
Trigger:Gram:('not',)
Transformation:SubSlot: ('*=*', '*!=*', 'left')
 -------------------------------------------------------------
Rule:3:Occ:4:Net:2
Trigger:Gram:('sv_near-0',)
Transformation:AddSlot:near="sv_near-0"
-------------------------------------------------------------
Rule:4:Occ:2:Net:2
Trigger:Gram:('sv_drinks-1',)
Transformation:AddSlot:drinks!="sv_drinks-1"
```

The file **debug-test.sem.hyp** contains the output of the TBL parser for the test set.
In the ideal case, it would be the same as the original test file **debug-test.sem**.

The file **debug-test.sem.hyp.algn** describes how the words (lexical realizations of slot values) were aligned with the slot values.

The file **debug-test.sem.hyp.anlz** provides list of parsing errors and explanation of the parsing process.
```
********************************************************************************
Substituted slot items (precision error)
*******************************************************

Substituted slot item: near!="sv_near-0" => near="sv_near-0" Occurence: 1
================================================================================
Text:          it is not near castle and serve wine
DB Text:       it is not near sv_near-0 and serve sv_drinks-0 .
Subst value:    4 =>           ('castle', 'castle') = sv_near-0
Subst value:    7 =>               ('wine', 'wine') = sv_drinks-0
................................................................................
it is not near sv_near-0 and serve sv_drinks-0 .
 0  1   2    3         4   5     6           7 8
------=========================================
                              drinks="sv_drinks-0" (00,02,07,07) <= [1, 2, 7]
               ==========------------------------
                                  near="sv_near-0" (04,04,04,08) <= [4]
................................................................................
HYP Semantics: inform(drinks="sv_drinks-0",near="sv_near-0")
HYP Semantics: inform(drinks="wine",near="castle")
REF Semantics: inform(near!="sv_near-0",drinks="sv_drinks-0")
REF Semantics: inform(near!="castle",drinks="wine")
AppliedRules:  5
RULE:TRIGGER:Gram: None - SpeechAct: None - Slots: None - HasSlots: None - TRANS:SpeechAct: inform - AddSlot: None - DelSlot: None - SubSlot: None -
DA:AFTER:THE:RULE: inform()

RULE:TRIGGER:Gram: ('sv_drinks-0',) - SpeechAct: None - Slots: None - HasSlots: None - TRANS:SpeechAct: None - AddSlot: drinks="sv_drinks-0" - DelSlot: None - SubSlot: None -
DA:AFTER:THE:RULE: inform(drinks="sv_drinks-0")

RULE:TRIGGER:Gram: ('not',) - SpeechAct: None - Slots: None - HasSlots: None - TRANS:SpeechAct: None - AddSlot: None - DelSlot: None - SubSlot: ('*=*', '*!=*', 'left') -
DA:AFTER:THE:RULE: inform(drinks!="sv_drinks-0")

RULE:TRIGGER:Gram: ('sv_near-0',) - SpeechAct: None - Slots: None - HasSlots: None - TRANS:SpeechAct: None - AddSlot: near="sv_near-0" - DelSlot: None - SubSlot: None -
DA:AFTER:THE:RULE: inform(drinks!="sv_drinks-0",near="sv_near-0")

RULE:TRIGGER:Gram: ('is',) - SpeechAct: None - Slots: None - HasSlots: None - TRANS:SpeechAct: None - AddSlot: None - DelSlot: None - SubSlot: ('*!=*', '*=*', 'left') -
DA:AFTER:THE:RULE: inform(drinks="sv_drinks-0",near="sv_near-0")
--------------------------------------------------------------------------------
```

The file **debug-test.sem.hyp.rslt** stores list accuracy of TBL parser.
```
Precision error per act:  0.22 inform (2/9)

Recall error per act:  1.00 confirm (2/2)


Recall error per item:  0.20 drinks=wine (1/5)
Recall error per item:  0.50 drinks=beer (1/2)
Recall error per item:  1.00 near=castle (1/1)

total ref items = 12
total test items = 12

SemScore Results: Ref contains 9 acts; 13 items
---------------------------------------------
|  Act Type|      Item|      Item|      Item|
|  Accuracy| Precision|    Recall| F-measure|
---------------------------------------------
|     77.78|     75.00|     69.23|     72.00|
---------------------------------------------
```

# Next #

[Configuration of the experiment](ConfigurationOfTheExperiment.md)