#!/bin/sh
#$ -S /bin/bash

cp new.atis-dev.sem atis-dev.sem
cp new.atis-dev.sem.dep atis-dev.sem.dep
cp new.atis-test.sem atis-test.sem
cp new.atis-test.sem.dep atis-test.sem.dep
cp new.atis-train.sem atis-train.sem
cp new.atis-train.sem.dep atis-train.sem.dep

head -n 501 new.atis-train.sem > atis-train-500.sem
head -n 501 new.atis-train.sem.dep >atis-train-500.sem.dep

head -n 1000 new.atis-train.sem > atis-train-1000.sem
head -n 1000 new.atis-train.sem.dep >atis-train-1000.sem.dep
