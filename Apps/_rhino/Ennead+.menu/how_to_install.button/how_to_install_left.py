
__title__ = "HowToInstall"
__doc__ = "This button does HowToInstall when left click"

import webbrowser

from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def how_to_install():
    webbrowser.open('https://ei.ennead.com/page/486/EnneadTab-for-rhino-20-1-9')

if __name__ == "__main__":
    how_to_install()