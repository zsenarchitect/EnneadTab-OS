#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Update the life safety information data"
__title__ = "Update Life Safety Info"

# from pyrevit import forms #
from re import L
from pyrevit import script #


from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_LIFE_SAFETY, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

@ERROR_HANDLE.try_catch_error()
def update_life_safety(doc):
    data_source = REVIT_LIFE_SAFETY.SpatialDataSource(
                source = "Area",
                area_scheme_name = "Life Safety",
                 para_name_load_per_area = "Rooms_$LS_Occupancy AreaPer",
                 para_name_load_manual = "Rooms_$LS_Occupancy Load_Manual",
                 para_name_target = "Rooms_$LS_Occupancy Load_Target",
                 para_name_egress_id = "Door_$LS_Exit Name",
                 para_name_door_width = "Door_$LS_Clear Width"
                 )

    t = DB.Transaction(doc, "Life Safety Update")
    t.Start()
    REVIT_LIFE_SAFETY.update_life_safety(doc, data_source)


    purge_tags_on_non_egress()



    t.Commit()



def purge_tags_on_non_egress():
    
    family_type = REVIT_FAMILY.get_family_type_by_name("LS Door Data", "SD")
    #tags = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name("LS Door Data", "SD")
    tags = REVIT_SELECTION.get_all_instances_of_type(family_type)
    tags = [el for el in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_DoorTags).WhereElementIsNotElementType().ToElements() if el.GetTypeId() == family_type.Id]
    # print (tags)
    for tag in tags:
        host_refs = list(tag.GetTaggedReferences())
        if len(host_refs) == 0:
            continue
        for host_ref in host_refs:

            host = doc.GetElement(host_ref.ElementId) or doc.GetElement(host_ref.LinkedElementId)

            if not host.LookupParameter("Door_$LS_Exit Name") or not host.LookupParameter("Door_$LS_Exit Name").HasValue or host.LookupParameter("Door_$LS_Exit Name").AsString() == "":
                doc.Delete(tag.Id)
################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    update_life_safety(doc)
    







