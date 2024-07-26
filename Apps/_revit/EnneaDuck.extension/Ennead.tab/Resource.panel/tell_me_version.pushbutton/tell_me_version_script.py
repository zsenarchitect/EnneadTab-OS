#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Tell Me\nVersion"
__context__ = "zero-doc"

import proDUCKtion # pyright: ignore 

from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab import VERSION_CONTROL
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def tell_me_version():
    VERSION_CONTROL.show_last_success_update_time()




################## main code below #####################
if __name__ == "__main__":
    tell_me_version()







