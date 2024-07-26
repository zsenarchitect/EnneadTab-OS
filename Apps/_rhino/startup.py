__title__ = "EnneadTab_Startup"
__doc__ = "Automatically run on every new rhino start session if bind to Rhino setting."
import os, sys
repos = [
        os.path.join(os.environ['USERPROFILE'] ,'github','EnneadTab-OS','Apps','lib'),
        os.path.join(os.environ['USERPROFILE'], 'dev-repo','EnneadTab-OS','Apps','lib'),
        os.path.join(os.environ['USERPROFILE'] , 'Documents','EnneadTab Ecosystem','EA_Dist','Apps','lib')
        ]
for repo in repos:
    if os.path.exists(repo):
        sys.path.append(repo)
        break

print ("\n".join(sys.path))
from EnneadTab import ERROR_HANDLE, NOTIFICATION, LOG, ENVIRONMENT, VERSION_CONTROL


import rhinoscriptsyntax as rs
import Rhino # pyright: ignore

sys.path.append(ENVIRONMENT.RHINO_FOLDER + "\\Ennead+.menu\\get_latest.button")
import get_latest_left


@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    VERSION_CONTROL.update_EA_dist()
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