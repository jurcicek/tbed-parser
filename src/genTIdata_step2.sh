#!/bin/sh
#$ -S /bin/bash

cp new.towninfo-dev.sem.dep towninfo-dev.sem.dep
cp new.towninfo-test.sem.dep towninfo-test.sem.dep
cp new.towninfo-train.sem.dep towninfo-train.sem.dep

cp new.towninfo-dev.asr.dep towninfo-dev.asr.dep
cp new.towninfo-test.asr.dep towninfo-test.asr.dep
cp new.towninfo-train.asr.dep towninfo-train.asr.dep

head -n 501 towninfo-train.sem > towninfo-train-500.sem
head -n 501 new.towninfo-train.sem.dep >towninfo-train-500.sem.dep

head -n 501 towninfo-train.asr > towninfo-train-500.asr
head -n 501 new.towninfo-train.asr.dep >towninfo-train-500.asr.dep
