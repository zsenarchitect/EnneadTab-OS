
__title__ = "SlopeCalculator"
__doc__ = "This button does SlopeCalculator when left click"
import webbrowser

from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def slope_calculator():
    path = "https://rechneronline.de/slope/"
    webbrowser.open(path)

if __name__ == "__main__":
    slope_calculator()