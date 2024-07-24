from pyrevit import EXEC_PARAMS
import proDUCKtion # pyright: ignore 
from EnneadTab import VERSION_CONTROL, ERROR_HANDLE
from EnneadTab.REVIT import REVIT_SYNC
import random

doc = EXEC_PARAMS.event_args.Document

def remove_last_sync_data_file(doc):
    REVIT_SYNC.remove_last_sync_data_file(doc)



def update_pyrevit():
    # occasionally update the pyrevit. Do it here becasue normally when you close doc you are relaxed and not care if it take too long
    if random.random() > 0.01:
        return
        
    from pyrevit.versionmgr import updater
    if updater.check_for_updates():
        updater.update_pyrevit()

@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    remove_last_sync_data_file(doc)
    update_pyrevit()
    VERSION_CONTROL.update_EA_dist()


###################################################
if __name__ == '__main__':
    main()
    
    
