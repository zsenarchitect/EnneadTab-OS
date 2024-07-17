
__title__ = "DVD"
__doc__ = "When you are bored..."

from EnneadTab.FUN import JOKES
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def dvd():
    JOKES.prank_dvd()

if __name__ == "__main__":
    dvd()