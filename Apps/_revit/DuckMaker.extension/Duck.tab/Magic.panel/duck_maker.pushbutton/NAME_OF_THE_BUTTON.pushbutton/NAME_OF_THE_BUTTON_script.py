#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "PRETTY_NAME"

import proDUCKtion # pyright: ignore 

from EnneadTab import ERROR_HANDLE, LOG
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()


# @LOG.use_enneadtab(coin_change = 20, tool_used = __title__, show_toast = True)
# @ERROR_HANDLE.try_catch_error
def NAME_OF_THE_BUTTON():
    pass


    t = DB.Transaction(DOC, __title__)
    t.Start()
    pass
    t.Commit()



################## main code below #####################
if __name__ == "__main__":
    NAME_OF_THE_BUTTON()







