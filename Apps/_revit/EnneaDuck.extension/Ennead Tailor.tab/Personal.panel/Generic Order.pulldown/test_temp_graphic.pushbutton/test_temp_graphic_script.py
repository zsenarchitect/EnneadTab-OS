#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "test_temp_graphic"

# from pyrevit import forms #
from pyrevit import script #


from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW
from Autodesk.Revit import DB # pyright: ignore 
import os
"""note: make it 64x64
open in MS paint and save as 16 bit color bmp
background 0,128,128
"""

# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error()
def test_temp_graphic():

    REVIT_VIEW.show_in_convas_graphic(DB.XYZ(400,150,50), additional_info={"description":"Hello"})


    return
    manager = DB.TemporaryGraphicsManager.GetTemporaryGraphicsManager(doc)
    
    manager.Clear()

    

    # path = "C:\\Users\\szhang\\github\\EnneadTab-for-Revit\\ENNEAD.extension\\lib\\EnneadTab\\images\\ennead-e-logo.bmp"
    path = "C:\\Users\\szhang\\github\\EnneadTab-for-Revit\\ENNEAD.extension\\lib\\EnneadTab\\images\\warning_duck.bmp"
    if os.path.exists(path):
    
        data = DB.InCanvasControlData (path, DB.XYZ(0,0,0))
        manager.AddControl(data, doc.ActiveView.Id)

    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    test_temp_graphic()
    







