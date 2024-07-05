import rhinoscriptsyntax as rs
import Rhino # pyright: ignore


from EnneadTab import ERROR_HANDLE, NOTIFICATION, LOG, FOLDER, ENVIRONMENT, VERSION_CONTROL


import sys
sys.path.append(ENVIRONMENT.RHINO_FOLDER + "\\Ennead+.menu\\get_latest.button")
import get_latest_left


@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    add_hook()
    
    get_latest_left.get_latest(is_silient = True)

    NOTIFICATION.messenger(main_text = "Startup Script Completed")

    

def add_hook(): 
    # first record current file
    action_update_timesheet(Rhino.RhinoDoc.ActiveDoc)
   
        
    # then add hook for future file in this session
    Rhino.RhinoDoc.BeginOpenDocument += event_func_timesheet
    Rhino.RhinoDoc.CloseDocument += event_func_timesheet


    Rhino.RhinoDoc.BeginSaveDocument += event_func_update_EA_dist
###################################################
def action_update_timesheet(doc):
    if doc.Path:
        LOG.update_time_sheet_rhino(doc.Path)


##################################################
def event_func_timesheet(sender, e):
    action_update_timesheet(e.Document)

def event_func_update_EA_dist(sender, e):
    VERSION_CONTROL.update_EA_dist()

    


if __name__ == "__main__":
    main()