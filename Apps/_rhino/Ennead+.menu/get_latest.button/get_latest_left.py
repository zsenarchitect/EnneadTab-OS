
__alias__ = "GetLatest"
__doc__ = "This button does GetLatest when left click"

from EnneadTab import VERSION_CONTROL, NOTIFICATION
from EnneadTab.RHINO import RHINO_RUI


def get_latest(is_silient = False):

    VERSION_CONTROL.update_EA_dist()

    RHINO_RUI.update_my_rui()

    # register alias, including the starter

    if not is_silient:
        NOTIFICATION.messenger("Latest Loaded")


 



