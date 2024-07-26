
from Autodesk.Revit import DB # pyright: ignore 

from EnneadTab import ERROR_HANDLE

@ERROR_HANDLE.try_catch_error()
def create_worksets(doc, workset_names):
    t = DB.Transaction(doc, 'Create Worksets')
    t.Start()

    for name in workset_names:
        if not DB.WorksetTable.IsWorksetNameUnique(doc, name):
            print ("Workset name <{}> already exists. Skipping".format(name))
            continue
        DB.Workset.Create(doc, name)
        print ("Created Workset: {}".format(name))
    t.Commit()

if __name__== "__main__":
    pass