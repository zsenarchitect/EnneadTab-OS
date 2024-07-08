
__title__ = "PerforationRatio"
__doc__ = "Find out how to calculate your perforation panel with precise opening ratio."

import webbrowser
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def perforation_ratio():
    link = r"https://www.perforated-sheet.com/calculation/how-to-calculate-open-area.html#:~:text=Open%20area%20is%20a%20ratio,of%20the%20sheet%20is%20material."
    webbrowser.open(link)

if __name__ == "__main__":
    perforation_ratio()