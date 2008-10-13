#!/usr/bin/env python2.5

import pstats

p = pstats.Stats('trn.train.profile')

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
