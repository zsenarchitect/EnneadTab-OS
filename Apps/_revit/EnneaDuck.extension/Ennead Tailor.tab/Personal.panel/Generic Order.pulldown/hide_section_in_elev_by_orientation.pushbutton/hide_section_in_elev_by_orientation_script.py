#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Hide the wall section marks in elevations if its defined orientation does not match the orienation of the elevation. \n\nThis will resolve the issue of seeing wall section mark from the other side of the building, but you cannot change view depth per design reason."
__title__ = "Hide Section in Elevation by Orientation"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


ORIENTATION_PARA = "Orientation"

def process_view(view):
    print("\n##############")
    print("Processing view [{}]".format(view.Name))
    if view.LookupParameter(ORIENTATION_PARA) is None:
        print("No oritation parameter yet, skipping")
        return
    my_orientation = view.LookupParameter(ORIENTATION_PARA).AsString()
    if my_orientation == "" or not view.LookupParameter(ORIENTATION_PARA).HasValue:
        print("No oritation assigned to this view, skipping")
        return

    everything = DB.FilteredElementCollector(doc, view.Id).WhereElementIsNotElementType().ToElements()
    sections = filter(lambda x: x.Category is not None and x.Category.Name == "Views", everything)
    def is_same_orientation(section):
        #print section.Name
        #print doc.GetElement(section.Id).ViewType
        if section.LookupParameter(ORIENTATION_PARA).AsString() == "" or not section.LookupParameter(ORIENTATION_PARA).HasValue:
            return True# will keep unassigned view, so pretent no assigned view the same orienation as my view
        if section.Id == view.Id:
            return False
        if section.LookupParameter(ORIENTATION_PARA).AsString() == my_orientation:
            return True
        return False
    sections = filter(lambda x: not(is_same_orientation(x)), sections)

    count = len(sections)
    if count > 0:
        view.HideElements (EA_UTILITY.list_to_system_list([x.Id for x in sections]))
        for section in sections:
            print("\tHiding [{}]".format(section.Name))



def hide_section_in_elev_by_orientation():
    views = forms.select_views(multiple = True,
                                title = "Views to process. Orientation para name = {}".format(ORIENTATION_PARA))
    if not views:
        return




    t = DB.Transaction(doc, __title__)
    t.Start()
    map(process_view, views)
    t.Commit()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    hide_section_in_elev_by_orientation()
    
