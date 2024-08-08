#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Purge Subcategory(Danger)"
__title__ = "38_Purge SubC"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def fake_delete_subC(subC):
    global safety
    is_purgable = False
    print("***************[{0}]--->[{1}]".format(c.Name , sub_c.Name))
    t = DB.Transaction(doc, "temp")
    t.Start()
    try:
        removed_elements = doc.Delete(subC.Id)
        safety += 1
        is_purgable = True

    except Exception as e:
        pass
        # print (e)
    finally:
        t.Commit()
        # t.RollBack()

    if not is_purgable:
        return

    print(removed_elements.Count)
    for id in list(removed_elements):
        graphic_style = doc.GetElement(id)
        print(graphic_style)
        # print graphic_style.GetType()
        # print graphic_style.Name #, graphic_style.GraphicsStyleCategory, graphic_style.GraphicsStyleType , graphic_style.GetDependentElements()


################## main code below #####################
output = script.get_output()
output.close_others()

"""
https://boostyourbim.wordpress.com/2016/10/21/purge-unused-materials-for-another-rtceur-api-wish/
"""

tg = DB.TransactionGroup(doc, "purge unused")
tg.Start()
safety = 0
all_Cs = doc.Settings.Categories
for c in all_Cs:
    if safety > 10:
        break
    for sub_c in c.SubCategories:

        fake_delete_subC(sub_c)


tg.RollBack()
