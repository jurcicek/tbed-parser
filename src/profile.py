#!/usr/bin/env python2.5

import pstats
import getopt, sys

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hp", 
        ["profileFile="])
         
except getopt.GetoptError, exc:
    print("ERROR: " + exc.msg)
    usage()
    sys.exit(2)

profileFile = 'trn.train.profile'

for o, a in opts:
    if o == "-h":
        usage()
        sys.exit()
    elif o == "--profileFile":
        profileFile = a

p = pstats.Stats(profileFile)

print '--------------------------------------------------------'

p.strip_dirs().sort_stats('cumulative').print_stats(30)

print '--------------------------------------------------------'
p.strip_dirs().sort_stats('time').print_stats(30)

print '--------------------------------------------------------'
p.strip_dirs().sort_stats('time').print_callers('len')
p.strip_dirs().sort_stats('time').print_callers('copy')

print '--------------------------------------------------------'
p.strip_dirs().sort_stats('time').print_callees('measure')
p.strip_dirs().sort_stats('time').print_callees('apply')
