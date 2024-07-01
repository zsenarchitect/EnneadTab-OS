
__alias__ = "GetLatest"
__doc__ = "This button does GetLatest when left click"

from EnneadTab import VERSION_CONTROL

def get_latest():

    VERSION_CONTROL.install_EA_dist()


    # save as curent rui to temp .rui so when closed it will not try to override the one from EA_ditst

    # close temp rui, pick up rui from dist folder

