#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Transfer the data between issing parameter and titleblock revision schedule. Also can transfer issue data from last round to current round."
__title__ = "Set Revision By BlackSquare"


from pyrevit import script

import System

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore  
# from Autodesk.Revit import UI # pyright: ignore
try:
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
except:
    pass


def get_revision_by_name(revision_name):

    revisions = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Revisions).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: revision_name == x.Description.split(" - ")[-1] , revisions)[0]


REF_MAP = {"Sheet_$Issue_SD": get_revision_by_name("100% Schematic Design")}
print (REF_MAP)



def set_revision_on_sheet(sheet):

    if not EnneadTab.REVIT.REVIT_SELECTION.is_changable(sheet):
        print ("Skipping sheet owned by someone else")

    new_revision_list = []
    
    for para in sheet.Parameters:
        if "Sheet_$Issue" in para.Definition.Name:
            if not para.HasValue:
                value = False
            
            else:
                value = len(para.AsString())
                
            if para.Definition.Name == "Sheets_$Issue_SD" and value:
                value = True
            
            
            if value and REF_MAP.has_key(para.Definition.Name):
                new_revision_list.append(REF_MAP[para.Definition.Name])
            
        
    collection = System.Collections.Generic.List[DB.ElementId]([x.Id for x in new_revision_list])
    #print collection
    sheet.SetAdditionalRevisionIds(collection)
    print ("Changing Revision on Sheet:{}".format(sheet.SheetNumber))



            
def main():

    # revision_names = [x.split("-----")[0] for x in raw_data]
    # para_names = [x.split("-----")[1] for x in raw_data]

    sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()




    t = DB.Transaction(doc, "Set Revision")
    t.Start()
    map(set_revision_on_sheet, sheets)
    t.Commit()



    print ("Tool Finished")
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()



