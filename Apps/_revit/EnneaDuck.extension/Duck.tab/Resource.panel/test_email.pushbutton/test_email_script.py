#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Test Email"

import proDUCKtion # pyright: ignore 

from EnneadTab import ERROR_HANDLE, LOG, EMAIL
# from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 

# UIDOC = REVIT_APPLICATION.get_uidoc()
# DOC = REVIT_APPLICATION.get_doc()


@ERROR_HANDLE.try_catch_error()
@LOG.log_revit
def test_email():
    EMAIL.email_to_self(body="123")


    # t = DB.Transaction(DOC, __title__)
    # t.Start()
    # pass
    # t.Commit()



################## main code below #####################
if __name__ == "__main__":
    test_email()







