#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py':
        continue

    if module in ["EnneaDuck"]:
        try:
            __import__(module, locals(), globals())
            continue
        except ImportError:
            pass

    if module[-3:] != '.py':
        continue
    try:
        __import__(module[:-3], locals(), globals())
    except Exception as e:
        # print(e)
        # print("Cannot import {}".format(module))
        pass
del module  # delete this varible becaue it is refering to last item on the for loop#!/usr/bin/python
