#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Test Core Module"

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def test_core_module():
    from EnneadTab import FOLDER
    path = FOLDER.get_EA_dump_folder_file("dss.test")
    print (path)

    from EnneadTab import ENVIRONMENT

    from EnneadTab import EMAIL
    EMAIL.email_to_self(body = "123")
    
    # from EnneadTab import UNIT_TEST
    # UNIT_TEST.test_core_module()




    # t = DB.Transaction(DOC, __title__)
    # t.Start()
    # pass
    # t.Commit()



################## main code below #####################
if __name__ == "__main__":
    test_core_module()







