from pyrevit import EXEC_PARAMS
from pyrevit.coreutils import envvars
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, FOLDER
from EnneadTab.REVIT import REVIT_FORMS, REVIT_EVENT





def check_is_template_folder():
    if REVIT_EVENT.is_L_drive_alert_hook_depressed:
        return
    path = EXEC_PARAMS.event_args.PathName
    extension = FOLDER.get_file_extension_from_path(path)
    #print extension
    if extension not in [".rft", ".rfa"]:
        return
    if r"L:\4b_Applied Computing\01_Revit\02_Template" in path or r"L:\4b_Applied Computing\01_Revit\03_Library" in path:
        REVIT_FORMS.notification(self_destruct = 5,main_text = "This family is currently saved in L drive\nRepath to your project folder to avoid affecting the original.", sub_text = path)

@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    check_is_template_folder()

##########################################

if __name__ == '__main__':
    main()