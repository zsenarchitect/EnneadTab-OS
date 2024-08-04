import os
import sys
import time
import rhinoscriptsyntax as rs
import Rhino # pyright: ignore




def add_search_path():
    for path in rs.SearchPathList():
        if 'EnneadTab-OS' in path:
            rs.DeleteSearchPath(path)
    _app_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib_path = os.path.join(_app_folder, "lib" )
    rs.AddSearchPath(lib_path)
    sys.path.append(lib_path)
    sys.path = list(set(sys.path))
      
time_start = time.time()
add_search_path()
print ("Get Latest use {:.2}s".format(time.time() - time_start))
print ("\n".join(sys.path))




__title__ = "GetLatest"
__doc__ = "Get the lastest version of EnneadTab"
__FONDATION__ = True
from EnneadTab import ERROR_HANDLE
from EnneadTab import VERSION_CONTROL, NOTIFICATION, LOG,ERROR_HANDLE
from EnneadTab.RHINO import RHINO_RUI, RHINO_ALIAS


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def get_latest(is_silient = False):

    VERSION_CONTROL.update_EA_dist()
    RHINO_RUI.update_my_rui()
    RHINO_ALIAS.register_alias_set()
    add_startup_script()
    update_GH_folders()


    if not is_silient:
        NOTIFICATION.messenger("Latest EnneadTab-For-Rhino Loaded")


def add_startup_script():
    
    """hear me out here:
    python cannot add startup script directly
   
    i use this python script C to call rhino script B to call rhino script A, which is the command alias
    This will not run the startup command, it just add to the start sequence.
    """
    rvb_satrtup_modifier_script = "{}\\StartupEnable.rvb".format(os.path.dirname(__file__))
    Rhino.RhinoApp.RunScript("-LoadScript " + rvb_satrtup_modifier_script, True)
 
def update_GH_folders():
    pass

    # check local component folder, compare to EA GH requirement list
    # if not exist, copy over.
    



if __name__ == "__main__":
    get_latest()