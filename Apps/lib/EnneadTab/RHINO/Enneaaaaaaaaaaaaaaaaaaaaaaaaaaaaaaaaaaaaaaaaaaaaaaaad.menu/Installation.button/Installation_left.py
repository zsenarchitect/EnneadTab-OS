
__title__ = "Install EnneadTab"
__doc__ = "Install EnneadTab"
__FONDATION__ = True

from EnneadTab import ERROR_HANDLE, LOG, ENVIRONMENT


import sys
sys.path.append(ENVIRONMENT.RHINO_FOLDER + "\\Ennead+.menu\\get_latest.button")
import get_latest_left

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()()
def Installation():
    get_latest_left.get_latest(is_silient = False)
