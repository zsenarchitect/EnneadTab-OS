__title__ = "EnneadTab_Startup"
__doc__ = "Automatically run on every new rhino start session if bind to Rhino setting."
import os, sys
_app_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_lib_path = os.path.join(_app_folder, "lib" )
sys.path.append(_lib_path)

# print ("\n".join(sys.path))
from EnneadTab import ERROR_HANDLE, NOTIFICATION, LOG, ENVIRONMENT, VERSION_CONTROL


import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
rs.AddSearchPath(_lib_path)

sys.path.append(ENVIRONMENT.RHINO_FOLDER + "\\Ennead+.menu\\get_latest.button")
import get_latest_left # pyright: ignore


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
        try:
            LOG.update_time_sheet_rhino(doc.Path)
        except:
            print ("Error updating timesheet")


##################################################
def event_func_timesheet(sender, e):
    action_update_timesheet(e.Document)

def event_func_update_EA_dist(sender, e):
    VERSION_CONTROL.update_EA_dist()

    


if __name__ == "__main__":
    main()