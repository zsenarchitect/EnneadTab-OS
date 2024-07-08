
__title__ = "GetLatest"
__doc__ = "This button does GetLatest when left click"

import EnneadTab
reload(EnneadTab)
from EnneadTab import VERSION_CONTROL, NOTIFICATION, LOG,ERROR_HANDLE
from EnneadTab.RHINO import RHINO_RUI

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def get_latest(is_silient = False):

    VERSION_CONTROL.update_EA_dist()

    RHINO_RUI.update_my_rui()


    # register alias, including the starter
    

    # add lib folder as search path

    if not is_silient:
        NOTIFICATION.messenger("Latest EnneadTab-For-Rhino Loaded")


 



