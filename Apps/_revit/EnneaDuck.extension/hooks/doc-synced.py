from pyrevit import EXEC_PARAMS
from Autodesk.Revit import DB # pyright: ignore


from pyrevit.coreutils import envvars
doc = EXEC_PARAMS.event_args.Document
import random

from EnneadTab import ERROR_HANDLE, SOUND

REGISTERED_AUTO_PROJS = ["1643_lhh bod-a_new",
                         "1643_lhh_bod-a_existing",
                        "2151_a-nyuli_hospital",
                        "Facade System"]

REGISTERED_AUTO_PROJS = [x.lower() for x in REGISTERED_AUTO_PROJS]

def warn_non_enclosed_area():
    areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()
    bad_areas = filter(lambda x: x.Area == 0, areas)
    if len(bad_areas) > 0:

        NOTIFICATION.toast(sub_text = "They might have impact on the accuracy of your Area Schedule.", main_text = "There are {} non-placed/redundant/non-enclosed areas in the file.".format(len(bad_areas)))


def warn_non_enclosed_room():
    rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()
    bad_rooms = filter(lambda x: x.Area == 0, rooms)
    if len(bad_rooms) > 0:

        NOTIFICATION.toast(sub_text = "A bad room might be either non-placed/redudent/non-enclosed.", main_text = "There are {} bad rooms in need of attention.".format(len(bad_rooms)))




def update_project_2151():
    # "ea_healthcare_r22 wip"
    if doc.Title.lower() not in ["2151_a-nyuli_hospital"]  :
        return
    
    folder = "Ennead Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "color_pills"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
    
    
    
    folder = "Ennead Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "all_in_one_checker"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)



    if USER_CONSTANTS.USER_NAME != "sha.li":
        return
    if random.random() > 0.1:
        return
    folder = "Ennead Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "confirm_RGB"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)


def update_project_2314():

    if "2314_a-455 1st ave" not in doc.Title.lower():
        return
    
    folder = "Ennead Tailor.tab\\Proj. 2314.panel\\First Ave.pulldown"
    func_name = "all_in_one_checker"
    

    
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
    
    return


def update_project_1643():
    update_new()
    update_existing()


def update_new():
    if "1643_lhh bod-a_new" not in doc.Title.lower():
        return


    folder = "Ennead Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_level_relative_value"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    
    folder = "Ennead Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_keyplan"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)



def update_existing():
    if "1643_lhh bod-a_existing" not in doc.Title.lower():
        return


    folder = "Ennead Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_grid_bldgId"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    folder = "Ennead Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_level_relative_value"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    folder = "Ennead Tailor.tab\\Proj. Lenox Hill.panel\\Lenox Hill.pulldown"
    func_name = "update_keyplan"
    MODULE_HELPER.run_revit_script(folder, func_name, doc)

    
def update_with_generic_healthcare_tool():
    if not USER.is_SZ():
        return
    health_care_projects = ["2151_a-nyuli_hospital"]
    
    if doc.Title.lower() not in health_care_projects:
        return
    
    folder = "Ennead.tab\\Tools.panel"
    func_name = "generic_healthcare_tool"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)


    
def update_DOB_numbering():
    folder = "Ennead.tab\\ACE.panel"
    func_name = "update_DOB_page"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)


def update_sheet_name():

    try:
        if doc.Title.lower() not in REGISTERED_AUTO_PROJS:
            return
    except:
        return
    

    
    script = "Ennead.tab\\Tools.panel\\general_renamer.pushbutton\\general_renamer_script.py"
    func_name = "rename_views"
    sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
    is_default_format = True
    show_log = False
    MODULE_HELPER.run_revit_script(script, func_name, doc, sheets, is_default_format, show_log)

    
def update_working_view_name():

    try:
        if doc.Title.lower() not in REGISTERED_AUTO_PROJS:
            return
    except:
        return
    
    
    script = "Ennead.tab\\Manage.panel\\working_view_cleanup.pushbutton\\manage_working_view_script.py"
    func_name = "modify_creator_in_view_name"

    fullpath = "{}\\ENNEAD.extension\\{}".format(ENVIRONMENT.PUBLISH_FOLDER_FOR_REVIT, script)
    import imp
    ref_module = imp.load_source("manage_working_view_script", fullpath)



    
    views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    no_sheet_views = filter(ref_module.is_no_sheet, views)
    is_adding_creator = True
    MODULE_HELPER.run_revit_script(script, func_name, no_sheet_views, is_adding_creator)
    

def update_project_2306():
    if "universal hydrogen" not in doc.Title.lower():
        return


    folder = "Ennead Tailor.tab\\Proj. 2306.panel\\Universal Hydro.pulldown"
    func_name = "factory_internal_check"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
 
    

def update_sync_queue():

    # dont need to do anything if pre-sycn chech was cancelled,
    if envvars.get_pyrevit_env_var("IS_SYNC_CANCELLED"):
        return

    log_file = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Sync_Queue\Sync Queue_{}.queue". format(doc.Title)
  

    try:
        with open(log_file, "r"):
            pass
    except:
        with open(log_file, "w+"): # if not existing then create
            pass

    queue = EA_UTILITY.read_txt_as_list(log_file)

    autodesk_user_name = EA_UTILITY.get_application().Username
    user_name = USER.get_user_name()
    OUT = []


    for item in queue:
        if user_name in item or autodesk_user_name in item:
            #this step remove current user name from any place in wait list, either beginging or last
            continue
        OUT.append(item)
        
        
    try:
        EA_UTILITY.save_list_to_txt(OUT, log_file)
    except:
        print ("Your account have no access to write in this address.")
        return

    if envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED"):
        # when  gloabl sync queue disabled, dont want to see dialogue, but still want to clear name from log file
        return

    if len(OUT) == 0:
        return
    try:
        next_user = OUT[0].split("]")[-1]
        # next user found!! if this step can pass
    except Exception as e:
        EA_UTILITY.print_note("cannot find next user.")
        EA_UTILITY.print_note(e)
        EA_UTILITY.print_traceback()
        return


    EMAIL.email(receiver_email_list="{}@ennead.com".format(next_user),
                            subject="Your Turn To Sync!",
                            body="Hi there, it is your turn to sync <{}>!".format(doc.Title),
                            body_image_link_list=["L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published\\ENNEAD.extension\\lib\\EnneadTab\\images\\you sync first.jpg"])

    REVIT.REVIT_FORMS.notification(main_text = "[{}]\nshould sync next.".format(next_user), sub_text = "Expect slight network lag between SH/NY server to transfer waitlist file.", window_width = 500, window_height = 400, self_destruct = 15)



def play_success_sound():
    file = 'sound_effect_mario_1up.wav'
    SOUND.play_sound(file)


def play_text_to_speech_audio():

    SPEAK.speak("Document {} has finished syncing.".format(doc.Title))


def update_sync_time_record():

    script_subfolder = "Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton\\update_last_sync_datafile_script.py"
    func_name = "update_last_sync_data_file"
    MODULE_HELPER.run_revit_script(script_subfolder, func_name, doc)
    
    func_name = "run_exe"
    MODULE_HELPER.run_revit_script(script_subfolder, func_name)



@ERROR_HANDLE.try_catch_error_silently
def main():

    
    play_success_sound()
    # update_sync_time_record()


    # if random.random() < 0.3:
    #     warn_non_enclosed_area()
    #     warn_non_enclosed_room()
    # output = script.get_output()
    # output.close_others(all_open_outputs = True)



    # update_project_2314()
    # update_project_2306()
    # update_project_2151()
    # update_project_1643()

    # update_with_generic_healthcare_tool()

    # update_DOB_numbering()

    # update_sync_queue()


    # ENNEAD_LOG.warn_revit_session_too_long(non_interuptive = False)

    # if ENNEAD_LOG.is_money_negative():
    #     print ("Your Current balance is {}".format(ENNEAD_LOG.get_current_money()))

    # ENNEAD_LOG.update_local_warning(doc)


    
    # update_sheet_name()
    # update_working_view_name()
    
    # play_text_to_speech_audio()





#################################################################
if __name__ == "__main__":
    main()
