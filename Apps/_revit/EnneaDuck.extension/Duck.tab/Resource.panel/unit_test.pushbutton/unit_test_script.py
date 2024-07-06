#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Unit Test"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore 

from Duckitect import ERROR_HANDLE, UNIT_TEST, LOG


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def unit_test():
    UNIT_TEST.test_core_module()



################## main code below #####################
if __name__ == "__main__":
    unit_test()







