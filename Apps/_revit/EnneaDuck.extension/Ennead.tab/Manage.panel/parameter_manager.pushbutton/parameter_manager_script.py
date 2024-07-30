#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """Batch adding shared parameters to multiple project files. 
This can reduce mistake during manual operation of repeating task."""
__title__ = "Proj. Parameter\nBatch Adding"
__tip__ = True
from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE, LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
            

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def parameter_manager(doc):
    definitions = REVIT_SELECTION.pick_shared_para_definition(doc, select_multiple = True)

    if not definitions:
        return
    docs = REVIT_SELECTION.pick_top_level_docs()
    if not docs:
        return
    cate_list = [("OST_Grids", "Grids"),
                ("OST_Levels", "Levels"),
                ("OST_Rooms", "Rooms"),
                ("OST_Areas", "Areas"),
                ("OST_Furniture", "Furniture")]
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return self.item[1]

    cates = forms.SelectFromList.show([MyOption(cate) for cate in cate_list], 
                                      title = "Select Categorie(s) to bind", 
                                      multiselect = True)
    if not cates:
        return
    
    cate_ids = [getattr(DB.BuiltInCategory , cate[0]) for cate in cate_list]
    cates = [DB.Category.GetCategory(doc, cate_id) for cate_id in cate_ids]

    para_group_list = [(DB.BuiltInParameterGroup.PG_DATA, "Data"),
                       (DB.BuiltInParameterGroup.PG_DATA, "Data")]
    
  
    for doc in docs:
        t = DB.Transaction(doc, __title__)
        t.Start()
        for definition in definitions:
            # print definition
            bind_para(doc, definition, cates)
            print ("new shared parameter [{}] added to doc [{}]".format(definition.Name, doc.Title))
        t.Commit()

    print ("\n\nTool Finish!!!!")

def bind_para(doc, definition, cates):
    #print definition, definition.Name


    # create new shared para
    try:
        DB.SharedParameterElement.Create(doc, definition)
    except Exception as e:
        print ("doc = " + doc.Title)
        print(e)
        return


    # define category set, should be  OST_Sheets
    cate_sets = DB.CategorySet()
    for cate in cates:
        cate_sets.Insert(cate)


    #instance binding
    binding = DB.InstanceBinding()
    binding.Categories = cate_sets

    #doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_GREEN_BUILDING)
    #doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_IFC)
    doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_DATA)
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    parameter_manager(doc)
