#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Create 3D workset checking view in your working folder.\nEach workset will get a 3D view that only have this workset turned on.\n\nIf there are no 'Views_$Group' and 'Views_$Series' in the view parameter, such as the case in using other firm file setup, the tool will not introduce 'Views_$Group' and 'Views_$Series' to them, the new 3D workset views will be just using revit default '???' group."
__title__ = "3D Workset\nViews"
__tip__ = True
from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

def get_all_userworkset():
    worksets = DB.FilteredWorksetCollector(doc).ToWorksets()
    return filter(lambda x: x.Kind .ToString() == "UserWorkset", worksets)


def make_3D_views_from_workset():
    worksets = get_all_userworkset()
    #02_Working > Workset Check
    """
    for workset in worksets:
        print(workset.Name)
    """

    views = [create_view(x.Name) for x in worksets]
    for view, workset in zip(views, worksets):
        print( "---working on setting workset visibility for view: " + view.Name)
        view.SetWorksetVisibility(workset.Id, DB.WorksetVisibility.Visible)
        for other_workset in worksets:
            if other_workset == workset:
                continue
            view.SetWorksetVisibility(other_workset.Id, DB.WorksetVisibility.Hidden)


        try:
            view.LookupParameter("Views_$Group").Set("Ennead")
            view.LookupParameter("Views_$Series").Set("Workset Check  *⸜( •ᴗ• )⸝*")

         
        except:
            pass

    print ("\n\n All worksets created.")



def create_view(view_name):
    desired_name = "EnneadTab Workset View_" + view_name
    view = get_view_by_name(desired_name)
    if view is not None:
        return view
    print ("####creating new axon view for " + view_name)
    view = DB.View3D.CreateIsometric (doc, get_threeD_view_type().Id)
    view.Name = desired_name
    return view

def get_view_by_name(name):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    for view in all_views:
        if name == view.Name:
            return view
    return None

def get_threeD_view_type():
    view_family_types = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()
    return filter(lambda x: x.ViewFamily == DB.ViewFamily.ThreeDimensional, view_family_types)[0]


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    t = DB.Transaction(doc, "create view from workset")
    t.Start()
    make_3D_views_from_workset()
    t.Commit()
    


################## main code below #####################

if __name__ == "__main__":
    output = script.get_output()
    output.close_others()

    main()