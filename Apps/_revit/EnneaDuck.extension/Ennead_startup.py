
__title__ = "Startup"
import os
import sys

"""need to navigate to duckking lib first before it can auto detect further. 
This is special treatment for te startup script only"""
# Define the relative path to the "lib" directory (2 levels up, then into "lib")
relative_lib_path = os.path.join('..',  'KingDuck.lib')

# Convert the relative path to an absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.abspath(os.path.join(current_dir, relative_lib_path))

# Add the "lib" directory to sys.path
if lib_dir not in sys.path:
    sys.path.append(lib_dir)





import proDUCKtion # pyright: ignore 
proDUCKtion.validify()



import imp
import os
import random
import time

from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
from pyrevit import forms, script
from pyrevit.coreutils import envvars
from pyrevit import versionmgr

import System # pyright: ignore
from EnneadTab import NOTIFICATION, DATA_FILE, FOLDER, OUTPUT, TIME, VERSION_CONTROL
from EnneadTab import MODULE_HELPER, ERROR_HANDLE, USER, KEYBOARD, ENVIRONMENT, SOUND, DOCUMENTATION, LOG, IMAGE
from EnneadTab import JOKE, EMOJI, ENCOURAGING, HOLIDAY
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION, REVIT_EVENT


# need below for the C drive space check
import clr # pyright: ignore
clr.AddReference('System.IO')
from System.IO import DriveInfo # pyright: ignore


def check_minimal_version_for_enneadtab():
    v = versionmgr.get_pyrevit_version()

    desired_major = 4
    desired_minor = 8
    major, minor, patch = v.as_int_tuple()
    if major < desired_major or minor < desired_minor:
        NOTIFICATION.messenger("Please update pyrevit from self service port\n{}.{} ---> {}.{}".format(major, minor, desired_major, desired_minor))
        output = OUTPUT.get_output()

        output.write("Please update pyrevit from self service port!!!",OUTPUT.Style.Title)
        output.write("Your version: {}.{} ---> Suggested version: {}.{}".format(major, minor, desired_major, desired_minor),OUTPUT.Style.SubTitle)
        output.insert_division()
        output.write ("Did you know pyrevit 4.7 was released at end of 2019? That was so long ago Covid was not even a thing yet.")

        covid_img = IMAGE.get_one_image_path_by_prefix("covid_joke")
        output.write(covid_img)

        output.plot()


def annouce_hibration_mode():
    if random.random() > 0.000000001:
        return
    output = OUTPUT.get_output()
    if random.random() > 0.7:
        output.write("EnneadTab in hibernation mode.", OUTPUT.Style.Title) 
        output.write("Due to staffing plan change, Sen Zhang is no longer maintaining ")
        output.write("Bug-fix and feature-build are suspended.")
        output.write("{}\\hibernation_large.png".format(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        """https://www.fontspace.com/cobemat-cartoon-font-f104361
        this is the font webpage"""
    else:
        output.write("EnneaDuck is on vacation to get a tan.", OUTPUT.Style.Title) 
        output.write("He is not available at the moment, check back later.")
        output.write("{}\\beijing duck.jpg".format(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
    output.plot()








def open_scheduled_docs():
    """this will also require the exe to run a schedule to active the revit, with version required.
    """

    data_file = "action_" + "schedule_opener_data.sexyDuck"
    if not os.path.exists(FOLDER.get_EA_dump_folder_file(data_file)):
        return
    data = DATA_FILE.get_data(data_file)
    if not data:
        return
    
    begin_time = time.time()
    
    folder = "Ennead.tab\\Tools.panel"
    func_name = "open_doc_silently"
    

    success_docs_note = ""
    failed_docs_note = ""
    for doc in data["docs"]:
        try:
            MODULE_HELPER.run_revit_script(folder, func_name, [doc])
            # ref_module.Solution().main([doc])
            success_docs_note += "[{}]\n".format(doc)
        except:
            print ("Cannot open <{}>".format(doc))
            failed_docs_note += "[{}]\n".format(doc)
    

    
    # if so, check the GUID and open each one, use silent openner.
    
    os.remove(FOLDER.get_EA_dump_folder_file(data_file))
    used_time = time.time() - begin_time
    REVIT_FORMS.notification(main_text = "{} have been preloaded to this revit session.\nIt took {}.".format(success_docs_note, TIME.get_readable_time(used_time)),
                                             sub_text = "Even you are not seeing them right now, they hare been openned in the background.\nTo show them, open those files as normal(click from 'recently open list') to see them instantly open.")

    try:
        KEYBOARD.send_control_D()
    except:
        pass




def check_C_drive_space():
    drive = DriveInfo("C")
    percent_used = int(float(drive.TotalSize - drive.AvailableFreeSpace) / drive.TotalSize * 100)
    
    if percent_used > 85:
        NOTIFICATION.messenger(main_text = "Your C drive is almost full, {}% used.\nSome revit file might fail to open. Please clean cache with ".format(percent_used))
    else:
        NOTIFICATION.messenger(main_text = "Your C drive is {}% used.".format(percent_used))
            



def register_auto_update():
    from pyrevit.userconfig import user_config
    user_config.check_updates = True
    user_config.save_changes()






class TempGraphicServer(UI.ITemporaryGraphicsHandler):

    @ERROR_HANDLE.try_catch_error(is_silent=True)
    def OnClick(self, data):
        """this data is TemporaryGraphicsCommandData class that return during click,
        not InCanvasControlData class used to add control"""

        manager = DB.TemporaryGraphicsManager.GetTemporaryGraphicsManager(data.Document)
        manager.RemoveControl(data.Index)
        SOUND.play_sound("sound_effect_duck.wav")




        temp_graphic_data = DATA_FILE.read_json_as_dict_in_dump_folder("CANVAS_TEMP_GRAPHIC_DATA_{}.sexyDuck".format(data.Document.Title),
                                                                                 create_if_not_exist=True)
        record = temp_graphic_data.get(str(data.Index))
        if record and record.get("additional_info").get("description"):
            NOTIFICATION.messenger(record["additional_info"]["description"])
        
    def GetName(self):
        return "My Graphics Service"
        
    def GetDescription(self):
        return "This is a graphics service"
        
    def GetVendorId(self):
        return "EnneadTab"
        
    def GetServiceId(self):
        return DB.ExternalService.ExternalServices.BuiltInExternalServices.TemporaryGraphicsHandlerService
        
    def GetServerId(self):
        return System.Guid("a8debc37-19fe-4198-1198-01a891ff1a7f")

    
def register_temp_graphic_server():
    external_service = DB.ExternalService.ExternalServiceRegistry.GetService(
        DB.ExternalService.ExternalServices.BuiltInExternalServices.TemporaryGraphicsHandlerService
    )
    my_graphics_service = TempGraphicServer()
    if external_service.IsRegisteredServerId (my_graphics_service.GetServerId()):
        external_service.RemoveServer(my_graphics_service.GetServerId())
        NOTIFICATION.messenger("Remove old graphical server...")
    external_service.AddServer(my_graphics_service)
    external_service.SetActiveServers(System.Collections.Generic.List[System.Guid]([my_graphics_service.GetServerId()]))


def register_xaml_path():
    """go thru all extension to location all examl file location, so later when attempt o lokk up it is quicker."""
    data = {}

    # loop thru folder and nesting folder
    for root, dirs, files in os.walk(ENVIRONMENT.REVIT_FOLDER):
        for file in files:
            if file.endswith(".xaml"):
                data[file] = os.path.join(root, file)

    DATA_FILE.set_data(data, "xaml_path.sexyDuck")
    


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error(is_silent=True)
def EnneadTab_startup():
    VERSION_CONTROL.update_EA_dist()
    register_xaml_path()
    check_minimal_version_for_enneadtab()
    ENCOURAGING.warming_quote()

    NOTIFICATION.duck_pop(main_text = "Hello {}!\nEnneaDuck welcome you back!".format(USER.get_user_name() ))
    

    HOLIDAY.festival_greeting()
    
    check_C_drive_space()

    if random.random() > 0.2:
        DOCUMENTATION.tip_of_day()

  
        
    
    
    
    # use this part to force clear a user from database, in case the file is corrupted
    # ENNEAD_LOG.force_clear_user(target_user_names = ["fliu"])
    
    # ENNEAD_LOG.open_revit_successful()
    
    # if ENNEAD_LOG.is_money_negative():
    #     print ("Your Current balance is {}".format(ENNEAD_LOG.get_current_money()))
    


    
    open_scheduled_docs()
    
    REVIT_EVENT.set_doc_change_hook_depressed(stage = False)
    REVIT_EVENT.set_sync_queue_enable_stage(stage = False)

    TIME.update_revit_uptime()


    

    register_auto_update()

    register_temp_graphic_server()




if __name__ == "__main__":
    EnneadTab_startup()

