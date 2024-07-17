import rhinoscriptsyntax as rs
import os
import sys
import Rhino # pyright: ignore


def add_search_path():
    repos = [
        os.path.join(os.environ['USERPROFILE'] ,'github','EnneadTab-OS','Apps','lib'),
        os.path.join(os.environ['USERPROFILE'], 'dev-repo','EnneadTab-OS','Apps','lib'),
        os.path.join(os.environ['USERPROFILE'] , 'Documents','EnneadTab Ecosystem','EA_Dist','Apps','lib')
        ]
    for path in rs.SearchPathList():
        # print ("Rhion sarch path", path)
        if path in repos:
            rs.DeleteSearchPath(path)
            
    for repo in repos:
        if os.path.exists(repo):
            rs.AddSearchPath(repo)
            sys.path.append(repo)
            return


add_search_path()





__title__ = "GetLatest"
__doc__ = "Get the lastest version of EnneadTab"
__FONDATION__ = True
import EnneadTab
reload(EnneadTab) # pyright: ignore
from EnneadTab import VERSION_CONTROL, NOTIFICATION, LOG,ERROR_HANDLE
from EnneadTab.RHINO import RHINO_RUI, RHINO_ALIAS


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def get_latest(is_silient = False):

    VERSION_CONTROL.update_EA_dist()
    RHINO_RUI.update_my_rui()
    RHINO_ALIAS.register_alias_set()
    add_search_path()
    add_startup_script()


    if not is_silient:
        NOTIFICATION.messenger("Latest EnneadTab-For-Rhino Loaded")


def add_startup_script():
    
    """hear me out here:
    python cannot add startup script directly
   
    i use this python script C to call rhino script B to call rhino script A, which is the command alias
    """
    rvb_satrtup_modifier_script = "{}\\StartupEnable.rvb".format(os.path.dirname(__file__))
    Rhino.RhinoApp.RunScript("-LoadScript " + rvb_satrtup_modifier_script, True)
 


if __name__ == "__main__":
    get_latest()