#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Unit Test"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore 

from EnneadTab import ERROR_HANDLE, UNIT_TEST, LOG


@ERROR_HANDLE.try_catch_error
@LOG.log
def unit_test():
    print (123)
    # UNIT_TEST.test_core_module()






################## main code below #####################
if __name__ == "__main__":
    unit_test()







