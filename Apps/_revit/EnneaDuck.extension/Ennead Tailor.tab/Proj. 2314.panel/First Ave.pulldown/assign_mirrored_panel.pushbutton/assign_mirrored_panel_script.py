#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "For Ethan's beautiful diagram."
__title__ = "Assign Mirrored Panels"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

FAMILY_NAMES_PREFIX = "CW-1"
PARA_NAME = "Mirrored"

@EnneadTab.ERROR_HANDLE.try_catch_error
def assign_mirrored_panel():
    # all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
    # families = [x for x in all_families if x.Name.startswith(FAMILY_NAMES_PREFIX)]
    # print( families)
    
    # panels = []
    all_panels = DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WhereElementIsNotElementType().ToElements()
    panels = [x for x in all_panels if x.Symbol.FamilyName.startswith(FAMILY_NAMES_PREFIX)]
    
    t = DB.Transaction(doc, __title__)
    t.Start()
    for panel in panels:
        para = panel.LookupParameter(PARA_NAME)
        if para:
            is_flipped = panel.HandFlipped
            wall = panel.Host
            if wall.Flipped:
                is_flipped = not is_flipped
                
                
            para.Set(is_flipped)
            note = "mirrored" if is_flipped else "unmirrored"
            panel.LookupParameter('Comments').Set(note)
                
        
    t.Commit()
    
    EnneadTab.NOTIFICATION.messenger(main_text="Done")

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    assign_mirrored_panel()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)



