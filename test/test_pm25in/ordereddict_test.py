#!/usr/bin/env python
# -*- coding-utf8 -*-

from collections import OrderedDict

c = OrderedDict()
a = {'a': 1, 'b': 2, 'c': 3}
b = ['a', 'b', 'c']

print a

for i in b:
    c[i] = a.get(i)

print c
