from pyrevit import EXEC_PARAMS

from EnneadTab import VERSION_CONTROL, MODULE_HELPER, ERROR_HANDLE
import random

doc = EXEC_PARAMS.event_args.Document

def remove_last_sync_data_file(doc):
    script_subfolder = 'Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton\\update_last_sync_datafile_script.py'
    func_name = 'remove_last_sync_data_file'
    MODULE_HELPER.run_revit_script(script_subfolder, func_name,doc)


def update_tab():
    # occasionally update the pyrevit. Do it here becasue normally when you close doc you are relaxed and not care if it take too long
    if random.random() > 0.01:
        return
        
    from pyrevit.versionmgr import updater
    if updater.check_for_updates():
        updater.update_pyrevit()

@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    remove_last_sync_data_file(doc)
    update_tab()
    VERSION_CONTROL.update_EA_dist()


###################################################
if __name__ == '__main__':
    main()
    
    
