#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Legacy, now do output panel"
__title__ = "54_Create Shared Para(Legacy)"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore





def bind_para(doc, definition):
    #print definition, definition.Name


    # create new shared para
    try:
        DB.SharedParameterElement.Create(doc, definition)
    except Exception as e:
        print("doc = " + doc.Title)
        print (e)
        return


    # define category set, should be  OST_Sheets
    cate_sets = DB.CategorySet()
    cate = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Sheets)
    cate_sets.Insert(cate)


    #instance binding
    binding = DB.InstanceBinding()
    binding.Categories = cate_sets

    #doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_GREEN_BUILDING)
    #doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_IFC)
    doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_DATA)



def create_shared_para(doc):
    definition = EA_UTILITY.pick_shared_para_definition(doc)
    docs = EA_UTILITY.select_top_level_docs()
    for doc in docs:
        t = DB.Transaction(doc, "add new shared para")
        t.Start()
        bind_para(doc, definition)
        t.Commit()
    print("new shared parameter [{}] added to docs:".format(definition.Name))
    for doc in docs:
        print("\n\t\t" + doc.Title)




################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":

    create_shared_para(doc)
