#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Reload\nEnneadTab"
__context__ = "zero-doc"


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
from pyrevit.loader import sessionmgr

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def reload_EnneadTab():

    sessionmgr.reload_pyrevit()



################## main code below #####################
if __name__ == "__main__":
    reload_EnneadTab()







