#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Assign Linked Views to PlanSet 7"

# from pyrevit import forms #
from pyrevit import script #


from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_VIEW, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


EAEC_VIEW_MAP = {
    "PS 7_A10B1_10_B1":None,
    "PS 7_A10B2_10_B2":None,
    "PS 7_A101_10_L1":None,
    "PS 7_A102_10_L2":None,
    "PS 7_A103_10_L3":"LEVEL 3_ED OPT 3_PHASE 3 - INFILL D",
    "PS 7_A104_10_L4":"LEVEL 4_IMAGING_PHASE 1B&2 - INFILL D",
    "PS 7_A105_10_L5 - MECH":"LEVEL 5_BED FLOOR_PHASE 1B&2 - INFILL D",
    "PS 7_A106_10_L6":"LEVEL 6_BED FLOOR_PHASE 1B&2 - INFILL D",
    "PS 7_A107_10_L7":"LEVEL 7_NICU_PHASE 1B&2 - INFILL D",
    "PS 7_A108_10_L8":"LEVEL 8_BED FLOOR_PHASE 1B&2 - INFILL D",
    "PS 7_A109_10_L9":"LEVEL 9_LDR_PHASE 1B&2 - INFILL D",
    "PS 7_A110_10_L10 - Podium Beds":"LEVEL 10_ORS_PHASE 1B&2- INFILL D - SET BACK",
    "PS 7_A110M_10_L10M":"LEVEL 10_ORSMEZZ",
    "PS 7_A111_10_L11":"LEVEL 11 PHASE 3 - INFILL D - SET BACK",
    "PS 7_A112_10_L12":"LEVEL 12 PHASE 1B&2 - INFILL D - SET BACK",
    "PS 7_A113_10_L13":"LEVEL 13_CSS PHASE 1B&2 - INFILL D",
    "PS 7_A114_10_L14 MECH":"LEVEL 14 - MECH",
    "PS 7_A115_10_L19":"LEVEL 19_40 BED FLOOR PLAN",
    "PS 7_A116_10_L21 MECH":None
}


@ERROR_HANDLE.try_catch_error()
def assign_linked_view():
    link = REVIT_SELECTION.get_revit_link_instance_by_name("20160364_LHH BOD-A_FO_New")
    if not link:
        print ("EC_NEW not found")
        return


    t = DB.Transaction(doc, __title__)
    t.Start()
    
    for ea_view in EAEC_VIEW_MAP.keys():
        view = REVIT_VIEW.get_view_by_name(ea_view)
        if not view:
            print (ea_view, "not found")
            continue

        link_view_name = EAEC_VIEW_MAP[ea_view]
        if not link_view_name:
            # EC not preparing those view, we do not need to link view
            continue
        link_view = REVIT_VIEW.get_view_by_name(link_view_name, doc = link.GetLinkDocument())
        if not link_view:
            print (link_view_name, "not found")
            continue

        

        link_graphic_setting = view.GetLinkOverrides (link.Id)
        if not link_graphic_setting:
            link_graphic_setting = DB.RevitLinkGraphicsSettings()
        link_graphic_setting.LinkVisibilityType  = DB.LinkVisibility .ByLinkView
        link_graphic_setting.LinkedViewId = link_view.Id
        view.SetLinkOverrides (link.Id, link_graphic_setting)

    t.Commit()

    NOTIFICATION.messenger("DONE!!!!!!!!")

################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    assign_linked_view()
    







