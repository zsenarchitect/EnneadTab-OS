import os
import random
from pyrevit import EXEC_PARAMS
from Autodesk.Revit import DB # pyright: ignore
from pyrevit.coreutils import envvars
doc = EXEC_PARAMS.event_args.Document


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, SOUND, LOG, NOTIFICATION, SPEAK, MODULE_HELPER, ENVIRONMENT, EMAIL, USER, DATA_FILE
from EnneadTab.REVIT import REVIT_SYNC, REVIT_FORMS, REVIT_EVENT
__title__ = "Doc Synced Hook"


REGISTERED_AUTO_PROJS = ["1643_lhh bod-a_new",
                         "1643_lhh_bod-a_existing",
                        "2151_a_ea_nyuli_cup_ext",
                        "2151_a_ea_nyuli_hospital_ext",
                        "2151_a_ea_nyuli_parking east",
                        "2151_a_ea_nyuli_parking west",
                        "2151_a_ea_nyuli_parking 1",
                        "2151_a_ea_nyuli_site",
                        "Facade System"]

REGISTERED_AUTO_PROJS = [x.lower() for x in REGISTERED_AUTO_PROJS]

def warn_non_enclosed_area():
    areas = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()
    bad_areas = filter(lambda x: x.Area == 0, areas)
    if len(bad_areas) > 0:

        NOTIFICATION.messenger("There are {} non-placed/redundant/non-enclosed areas in the file.\nThey might have impact on the accuracy of your Area Schedule.".format(len(bad_areas)))


def warn_non_enclosed_room():
    rooms = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()
    bad_rooms = filter(lambda x: x.Area == 0, rooms)
    if len(bad_rooms) > 0:

        NOTIFICATION.messenger("There are {} bad rooms in need of attention.\nA bad room might be either non-placed/redudent/non-enclosed.".format(len(bad_rooms)))





def update_project_2151():
    return
    
    # "ea_healthcare_r22 wip"
    if doc.Title.lower() not in ["2151_a_ea_nyuli_hospital_ext"]:
        return
    
    if random.random() > 0.1:
        return
    if USER_CONSTANTS.USER_NAME not in ["sha.li", "szhang"]:
        return
    
    folder = "Ennead Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "color_pills"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
    
    
    
    folder = "Ennead Tailor.tab\\Proj. 2151.panel\\LI_NYU.pulldown"
    func_name = "all_in_one_checker"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)



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
    if not USER.IS_DEVELOPER:
        return
    health_care_projects = ["2151_a_ea_nyuli_hospital_ext"]
    
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
        doc.Title
    except Exception as e:
        if USER.USER_NAME == "szhang":
            print (str(e))
        return


    if doc.Title.lower() not in REGISTERED_AUTO_PROJS:
        return

    script = "Ennead.tab\\Tools.panel\\general_renamer.pushbutton\\general_renamer_script.py"
    func_name = "rename_views"
    sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
    is_default_format = True
    show_log = False
    MODULE_HELPER.run_revit_script(script, func_name, doc, sheets, is_default_format, show_log)

    
def update_working_view_name():
    try:
        doc.Title
    except:
        return

    if doc.Title.lower() not in REGISTERED_AUTO_PROJS:
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
    # if not USER.is_SZ():
    #     return

    folder = "Ennead Tailor.tab\\Proj. 2306.panel\\Universal Hydro.pulldown"
    func_name = "factory_internal_check"
    MODULE_HELPER.run_revit_script(folder, func_name, doc, show_log = False)
 
    
    

def update_sync_queue():

    # dont need to do anything if pre-sycn chech was cancelled,
    if envvars.get_pyrevit_env_var("IS_SYNC_CANCELLED"):
        return

    log_file = "{}\\Sync_Queue\\Sync Queue_{}.sexyDuck". format(ENVIRONMENT.DB_FOLDER, doc.Title)
  

    if not os.path.exists(log_file):
        with open(log_file, "w+"): # if not existing then create
            pass

    queue = DATA_FILE.get_list(log_file)

    
    OUT = []


    for item in queue:
        if USER.USER_NAME in item:
            #this step remove current user name from any place in wait list, either beginging or last
            continue
        OUT.append(item)
        
        

    if not DATA_FILE.set_list(OUT, log_file):
        print ("Your account have no access to write in this address.")
        return

    if REVIT_EVENT.is_sync_queue_hook_depressed:
        # when  gloabl sync queue disabled, dont want to see dialogue, but still want to clear name from log file
        return

    if len(OUT) == 0:
        return
    try:
        next_user = OUT[0].split("]")[-1]
        # next user found!! if this step can pass
    except Exception as e:
        return


    EMAIL.email(receiver_email_list="{}@ennead.com".format(next_user),
                            subject="Your Turn To Sync!",
                            body="Hi there, it is your turn to sync <{}>!".format(doc.Title),
                            body_image_link_list=["L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published\\ENNEAD.extension\\lib\\EnneadTab\\images\\you sync first.jpg"])

    REVIT_FORMS.notification(main_text = "[{}]\nshould sync next.".format(next_user), sub_text = "Expect slight network lag between SH/NY server to transfer waitlist file.", window_width = 500, window_height = 400, self_destruct = 15)





    



def update_sync_time_record():

    
    script_subfolder = "Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton\\update_last_sync_datafile_script.py"
    func_name = "update_last_sync_data_file"
    MODULE_HELPER.run_revit_script(script_subfolder, func_name, doc)
    
    func_name = "run_exe"
    MODULE_HELPER.run_revit_script(script_subfolder, func_name)


def play_success_sound():
    file = 'sound_effect_mario_1up.wav'
    SOUND.play_sound(file)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error(is_silent=True)
def doc_synced():
    play_success_sound()

    REVIT_SYNC.update_last_sync_data_file(doc)
    update_sync_queue()
    

    if random.random() < 0.1:
        warn_non_enclosed_area()
    if random.random() < 0.1:
        warn_non_enclosed_room()

        
    update_DOB_numbering()
    update_sheet_name()
    update_working_view_name()
    update_with_generic_healthcare_tool()
    return


    update_project_2314()
    update_project_2306()
    update_project_2151()
    update_project_1643()






    ENNEAD_LOG.warn_revit_session_too_long(non_interuptive = False)





    if ENNEAD_LOG.is_money_negative():
        print ("Your Current balance is {}".format(ENNEAD_LOG.get_current_money()))

    ENNEAD_LOG.update_local_warning(doc)



    SPEAK.speak("Document {} has finished syncing.".format(doc.Title))
    
    
    envvars.set_pyrevit_env_var("IS_DOC_CHANGE_HOOK_ENABLED", True)
    



#################################################################
if __name__ == "__main__":
    doc_synced()
