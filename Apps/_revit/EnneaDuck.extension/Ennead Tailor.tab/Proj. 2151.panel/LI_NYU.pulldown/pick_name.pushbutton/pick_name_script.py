#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Pick your pill, then assign name from a list. Request by Gayatri"
__title__ = "Pick Name"

from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
            
COLOR_SCHEME_NAME = "[Areas]: Department Category_Primary"      
            
@EnneadTab.ERROR_HANDLE.try_catch_error
def pick_name():
    selection_ids = uidoc.Selection.GetElementIds ()
    if len (selection_ids) == 0:
        EnneadTab.NOTIFICATION.messenger(main_text = "Select one and only one pill shape")

        return 
    
    if len (selection_ids) != 1:
        EnneadTab.NOTIFICATION.messenger(main_text = "Select one and only one pill shape")
        return
    
    element = doc.GetElement(selection_ids[0])
    if not EnneadTab.REVIT.REVIT_SELECTION.is_changable(element):
        EnneadTab.NOTIFICATION.messenger(main_text = "You do not have permission to edit it.")
        return
    
    
    if not hasattr(element, "Symbol") or not element.Symbol.FamilyName.lower().startswith( "DTL_Healthcare_Planning_Section Bubble".lower()):
        EnneadTab.NOTIFICATION.messenger(main_text = "This tool only work with the pill shape")
        return
    
    
    color_schemes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ColorFillSchema).WhereElementIsNotElementType().ToElements()
    def scheme_name(x):
        cate_name = DB.Category.GetCategory(doc, x.CategoryId).Name
        return "[{}]: {}".format(cate_name, x.Name)
    
    color_schemes = filter(lambda x: scheme_name(x) == COLOR_SCHEME_NAME, color_schemes)
    if len( color_schemes)== 0:
        EnneadTab.NOTIFICATION.messenger(main_text = "Cannot find the color scheme [{}].\nMaybe you renamed your color scheme recently? Talk to SZ for update.".format(COLOR_SCHEME_NAME))
        return
    color_scheme = color_schemes[0]

    names = [entry.GetStringValue()  for entry in color_scheme.GetEntries()]
         
    name = forms.SelectFromList.show(sorted(names),
                                    multiselect=False)
    if not name:
        return
    # EnneadTab.NOTIFICATION.messenger(main_text = name)
    name = EnneadTab.TEXT.wrapped_text(name, max_len=20)
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    element.LookupParameter("bubble_diagram_label").Set(name)
    
    t.Commit()
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    pick_name()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)










