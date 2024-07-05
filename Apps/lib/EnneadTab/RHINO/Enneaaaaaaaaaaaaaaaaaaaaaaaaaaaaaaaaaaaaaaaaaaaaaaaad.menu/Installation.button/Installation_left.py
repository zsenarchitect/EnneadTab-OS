
__alias__ = "Install EnneadTab"
__doc__ = "Install EnneadTab"

from EnneadTab import ENVIRONMENT
import sys
sys.path.append(ENVIRONMENT.RHINO_FOLDER + "\\Ennead+.menu\\get_latest.button")
import get_latest_left

def Installation():
    get_latest_left.get_latest(is_silient = True)