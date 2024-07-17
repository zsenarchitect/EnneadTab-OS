# # Reference the Revit API
# import clr

# clr.AddReference('RevitAPI')
# clr.AddReference('RevitAPIUI')

from Autodesk.Revit import DB # pyright: ignore 
from pyrevit import forms

from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE
__title__ = "Create\nWorksets"
DEFAULT_LIST = ['0_References', 
                '0_Shared Levels & Grids', 
                '1_Core', 
                '1_FF&E', 
                '1_Shell', 
                '1_Interiors', 
                '1_Site', 
                '1_Structure',
                '2_RVT Links', 
                '3_CAD Links'] 
__doc__ = """Create Worksets following the standard Ennead Workset Structure.
You can the options to create any or all from below:"""
for item in DEFAULT_LIST:
    __doc__ += "\n+< " + item + " >"
__tip__ = True

# Obtain the document object
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


@ERROR_HANDLE.try_catch_error
def main():
    # # get all existing workset names
    # names = [ws.Name for ws in DB.FilteredWorksetCollector(doc) if ws.Kind == DB.WorksetKind.UserWorkset]
    # print names

    

    # return
    if not doc.IsWorkshared:
        print ("This document is not workshared. Cannot Create Worksets.")
        return
    # A list of workset names
    default_workset_names = DEFAULT_LIST
    selected_workset_names = forms.SelectFromList.show(default_workset_names,
                                                       title = "Select Ennead Standard Worksets To Add",
                                                       multiselect  = True)
    if not selected_workset_names:
        return
    

    t = DB.Transaction(doc, 'Create Worksets')

    t.Start()

    for name in selected_workset_names:
        if not DB.WorksetTable.IsWorksetNameUnique(doc, name):
            print ("Workset name <{}> already exists. Skipping".format(name))
            continue
        DB.Workset.Create(doc, name)
        print ("Created Workset: {}".format(name))

    t.Commit()

if __name__ == '__main__':
    main()
    
