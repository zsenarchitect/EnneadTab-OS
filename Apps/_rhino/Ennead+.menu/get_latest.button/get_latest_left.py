
__title__ = "GetLatest"
__doc__ = "This button does GetLatest when left click"
import os
import EnneadTab
reload(EnneadTab) # pyright: ignore
from EnneadTab import VERSION_CONTROL, NOTIFICATION, LOG,ERROR_HANDLE
from EnneadTab.RHINO import RHINO_RUI, RHINO_ALIAS

import rhinoscriptsyntax as rs

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def get_latest(is_silient = False):

    VERSION_CONTROL.update_EA_dist()
    RHINO_RUI.update_my_rui()
    RHINO_ALIAS.register_alias_set()
    add_search_path()


    if not is_silient:
        NOTIFICATION.messenger("Latest EnneadTab-For-Rhino Loaded")


 
def add_search_path():
    repos = [
        os.path.join(os.environ['USERPROFILE'] + '\\\\github\\\\EnneadTab-OS\\\\Apps\\\\lib'),
        os.path.join(os.environ['USERPROFILE'] + '\\\\dev-repo\\\\EnneadTab-OS\\\\Apps\\\\lib'),
        os.path.join(os.environ['USERPROFILE'] + '\\\\Documents\\\\EnneadTab Ecosystem\\\\EA_Dist\\\\Apps\\\\lib')
        ]
    for path in rs.SearchPathList():
        print ("Rhion sarch path", path)
        if path in repos:
            rs.DeleteSearchPath(path)
            
    for repo in repos:
        if os.path.exists(repo):
            rs.AddSearchPath(repo)
            return


if __name__ == "__main__":
    get_latest()