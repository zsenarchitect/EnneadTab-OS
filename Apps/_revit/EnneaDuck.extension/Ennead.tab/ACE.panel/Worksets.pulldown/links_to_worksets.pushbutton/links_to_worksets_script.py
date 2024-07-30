#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Links2Worksets"
__tip__ = True
# from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def links_to_worksets():


    all_revit_links = get_all_revit_links()
    for link in all_revit_links:
        link_type = doc.GetElement(link.GetTypeId())
        model_name = link_type.LookupParameter("Type Name").AsString()
        t = DB.Transaction(doc, "Set Model Worksets [{}]".format(model_name))
        t.Start()
        workset_name = "2_RVT Links_" + model_name.replace(".rvt", "").upper()
        existing_workset_id = get_workset_id(workset_name)
        link_type_workset = link_type.get_Parameter(DB.BuiltInParameter.ELEM_PARTITION_PARAM)
        link_workset = link.get_Parameter(DB.BuiltInParameter.ELEM_PARTITION_PARAM)
        if existing_workset_id is None:
            new_workset = DB.Workset.Create(doc, workset_name)
            link_type_workset.Set(new_workset.Id.IntegerValue)
            link_workset.Set(new_workset.Id.IntegerValue)
        else:
            link_type_workset.Set(existing_workset_id.IntegerValue)
            link_workset.Set(existing_workset_id.IntegerValue)
        t.Commit()

    pin_element_by_category(DB.BuiltInCategory.OST_RvtLinks)

    
def get_all_revit_links():
    collector = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_RvtLinks).OfClass(DB.RevitLinkInstance)
    return list(collector)

def pin_element_by_category(bic):
    elements = elements_of_specified_category(bic)
    if elements is None:
        return
    t = DB.Transaction(doc, "Pin all links")
    t.Start()
    for element in elements:
        if not element.Pinned:
            element.Pinned = True

    t.Commit()


def get_all_worksets():
    return DB.FilteredWorksetCollector(doc).OfKind(DB.WorksetKind.UserWorkset)

def get_workset_id(workset_name):
    if workset_name is None:
        return None
    worksets = get_all_worksets()
    for workset in worksets:
        if workset_name == workset.Name:
            return workset.Id
    return None

def elements_of_specified_category(bic):
    collector = DB.FilteredElementCollector(doc).OfCategory(bic)
    return list(collector)



################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    links_to_worksets()
    







