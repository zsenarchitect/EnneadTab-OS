#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Test Core Module"
__context__ = "zero-doc"
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, UNIT_TEST

from Autodesk.Revit import DB # pyright: ignore 



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def test_core_module():
    UNIT_TEST.test_core_module()

   
    



################## main code below #####################
if __name__ == "__main__":
    test_core_module()







