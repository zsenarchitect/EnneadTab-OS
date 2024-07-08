
__title__ = "ChinaCodeRef"
__doc__ = "This button does ChinaCodeRef when left click"
import subprocess
from EnneadTab import EXE, FOLDER
from EnneadTab.RHINO import RHINO_FORMS


def china_code_ref():
    folder = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Library Docs\\Codes"
    files = FOLDER.get_filenames_in_folder(folder)
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
    EXE.open_file_in_default_application(filepath)