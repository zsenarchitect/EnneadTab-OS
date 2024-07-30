
from pyrevit import EXEC_PARAMS
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_SYNC



########## main code below ############
# this varaible is set to True only after    use sync and close all is run ealier. So if user open new docs, we shoudl resume default False,


@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():

    doc = EXEC_PARAMS.event_args.Document


    if doc is None:
        return

    if doc.IsFamilyDocument:
        return
    
    
    REVIT_SYNC.update_last_sync_data_file(doc)






############################
if __name__ == "__main__":
    main()
