This section describes how to prepare an experiments. Every experiment has one configuration file in the "experiments" directory. It is simple shell script file which define several variables. Some of the variables are used by the **traisn** script. Some of them are just passed to the used training and decoding scripts.

# Configuration of the experiment #

The parameter of the **train** command is the path and the name to the configuration file of an experiment. The debug experiment has the following configuration file:
```
#!/bin/sh
#$ -S /bin/bash

export TBEDP_TRN_FILE=debug-train.sem
export TBEDP_TRN_DEP_FILE=""
export TBEDP_TST_SEM_FILE=debug-test.sem
export TBEDP_TST_SEM_DEP_FILE=""
export TBEDP_DEV_SEM_FILE=debug-dev.sem
export TBEDP_DEV_SEM_DEP_FILE=""

export TBEDP_DB_DIR=debug_db

export TBEDP_TRG_COND="{'nGrams':1, 'nStarGrams':1, 'speechAct':1, 'nSlots':1, 'hasSlots':0, 'DBItems':'replace', 'useDeps':0, 'nearestLeftPOSWord':0, 'nearestDepTreePOSWord':0, 'testLocality':1}"

```

  * The variables TBEDP\_TRN\_FILE, TBEDP\_TRN\_DEP\_FILE, TBEDP\_TST\_SEM\_FILE, TBEDP\_TST\_SEM\_DEP\_FILE, TBEDP\_DEV\_SEM\_FILE, TBEDP\_DEV\_SEM\_DEP\_FILE are used to inform the parser where training, development and testind data are. Each file can also have complementary file with dependency relationships between words and POS tags.
  * The variable TBEDP\_DB\_DIR says where the database with lexical realizations for slot items is stored.
  * The variable TBEDP\_TRG\_COND sets the training parameters of the TBL parser:
    * 'nGrams': 0 - no n-gram, 1 - unigrams only, 2 - unigrams and bigrams, 3 - up to trigrams, 4 - up to four grams, fourgrams is the maximum
    * 'nStarGrams': 0 - no skipping bigrams, 1 - skipping bigram skipping one word, 2,3 - skipping bigrams with up to 3 skipped words.
    * 'speechAct': 0 - do not use hypothesised dialogue act type in triggers, 1 - use it
    * 'nSlots': 0 - do not use hypothesised slots in triggers, 1 - use it
    * 'hasSlots': 0 - do not trigger on presence of slots, 1 - use it
    * 'DBItems':'replace': replace - replace lexical realizations of slot values with category labels, none - do nothing
    * 'useDeps': 0 - do not load and use `*`.dep files, 1 - use it
    * 'nearestLeftPOSWord': 0 - do not generate advanced lexical features using POS tags, 1 - use it
    * 'nearestDepTreePOSWord': 0 - do not use features generated from dependency trees which are in the `*`.dep files
    * 'testLocality': 0 - do not test locality of triggers of substitution operation, 1 - use it