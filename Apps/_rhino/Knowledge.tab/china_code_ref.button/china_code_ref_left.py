
__title__ = "ChinaCodeRef"
__doc__ = "This button does ChinaCodeRef when left click"
import os
import subprocess
from EnneadTab import EXE, FOLDER
from EnneadTab.RHINO import RHINO_FORMS

from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def china_code_ref():
    folder = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Library Docs\\Codes"
    files = os.listdir(folder)
    special_folder = "#PDF in this directory are reference only"
    files.remove(special_folder)

    keyword = "<Open Entire Code Folder...>"
    files.insert(0, keyword)

    selected_opt = RHINO_FORMS.select_from_list(files, multi_select = False, message = "WHAT THE CODE IS GOING ON?????")

    if not selected_opt:
        return


    if keyword == selected_opt:

        path = "file:\\L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Library Docs\DD Documentation Samples\\#PDF in this directory are reference only"
        subprocess.Popen('explorer /select, {}'.format(path))
        return

    filepath = folder + "\\" + selected_opt
    EXE.try_open_app(filepath)


if __name__ == "__main__":
    china_code_ref()