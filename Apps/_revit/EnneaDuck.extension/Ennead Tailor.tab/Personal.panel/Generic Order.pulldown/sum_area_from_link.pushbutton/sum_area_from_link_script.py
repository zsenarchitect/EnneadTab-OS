#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "sum_area_from_link"

# from pyrevit import forms #
from pyrevit import script #
from pyrevit import HOST_APP

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

def format_value(total, unit_type):
    format_options = doc.GetUnits().GetFormatOptions(unit_type)
    try:
        units = format_options.DisplayUnits
        label =  DB.LabelUtils.GetLabelFor(units)
    except AttributeError:
        units =  format_options.GetUnitTypeId()
        label =  DB.LabelUtils.GetLabelForUnit(units)
    return '{} {}'.format(
        DB.UnitUtils.ConvertFromInternalUnits(total, units),
        label)



def format_area(total):
    if HOST_APP.is_newer_than(2021):
        unit_type = DB.SpecTypeId.Area
    else:
        unit_type = DB.UnitType.UT_Area
    return format_value(total, unit_type)


@ERROR_HANDLE.try_catch_error
def sum_area_from_link():
    # from Autodesk.Revit.DB import *
    # from Autodesk.Revit.UI import *

    # Get the active Revit application and document
    app = __revit__.Application
    uidoc = __revit__.ActiveUIDocument

    sum = 0
    # Prompt the user to pick multiple linked elements
    try:
        refElemLinkedList = uidoc.Selection.PickObjects(UI.Selection.ObjectType.LinkedElement, "Please pick elements in the linked model")
    except:
        print ("No element selected")
        return
    # Iterate through the selected linked elements and retrieve corresponding elements from the linked documents
    for refElemLinked in refElemLinkedList:
        # Get the linked document
        linkedDoc = doc.GetElement(refElemLinked).GetLinkDocument()

        # Retrieve the element from the linked document
        elem = linkedDoc.GetElement(refElemLinked.LinkedElementId)

        # # Print element information
        # print("Element ID in linked document: {}".format(elem.Id))
        # print("Element name in linked document: {}".format(elem.Name))
        # print("Element category in linked document: {}".format(elem.Category.Name))

        # Get the area of the element
        sum += elem.Area

    print ("{} elements selected".format(len(refElemLinkedList)))
    print ("Sum of area is:")
    print (format_area(sum))


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    sum_area_from_link()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







