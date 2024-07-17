
from pyrevit import EXEC_PARAMS

from EnneadTab.MODULE_HELPER import run_revit_script
from EnneadTab.ERROR_HANDLE import try_catch_error_silently


def update_sync_time_record(doc):


    script_subfolder = "Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton\\update_last_sync_datafile_script.py"
    func_name = "update_last_sync_data_file"
    run_revit_script(script_subfolder, func_name, doc)

########## main code below ############
# this varaible is set to True only after    use sync and close all is run ealier. So if user open new docs, we shoudl resume default False,


@try_catch_error_silently
def main():

    doc = EXEC_PARAMS.event_args.Document


    if doc is None:
        return

    if doc.IsFamilyDocument:
        return
    
    
    update_sync_time_record(doc)






############################
if __name__ == "__main__":
    main()
