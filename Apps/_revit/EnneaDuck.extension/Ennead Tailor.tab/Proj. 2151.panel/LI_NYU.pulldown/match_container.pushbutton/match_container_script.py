#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Match Container"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_EVENT
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()
import container_file as CF

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def match_container():
    container_doc = CF.open_container_file()
    print (container_doc)

    # 

    


################## main code below #####################
if __name__ == "__main__":
    match_container()







