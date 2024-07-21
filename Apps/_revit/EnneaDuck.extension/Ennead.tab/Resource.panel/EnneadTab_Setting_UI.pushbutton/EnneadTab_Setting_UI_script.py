#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """All basic setting for the EnneadTab for Revit.
+Tabs avaliablity
+Tab Color.
+Switching between Lite and Pro version.
+Notification Setting.
+Duck Setting.
etc"""
__title__ = "EnneadTab\nSetting"
__context__ = "zero-doc"
__tip__ = [__doc__,
           "You can enjoy much more functions from the Ennead+ Version instead of staying in Lite Version."]

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException

import os
import System
import traceback


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import DATA_FILE, USER, NOTIFICATION, ENVIRONMENT, SPEAK, ERROR_HANDLE, FOLDER, IMAGE
from EnneadTab.FUN import EnneaDuck

from pyrevit import script, forms
from pyrevit.coreutils import ribbon
try:
    from pyrevit.revit import tabs as TABS
except:
    NOTIFICATION.messenger("Please update pyrevit to 4.8+.")





uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True



@ERROR_HANDLE.try_catch_error()
def change_extension_folder(is_force_tester, include_game):
    """this arg has no effect"""


    from pyrevit.userconfig import user_config
    from pyrevit.loader.sessionmgr import execute_command
    """Reads the user extension folders and updates the list"""
    current_external_folders = user_config.get_thirdparty_ext_root_dirs(include_default=False)
    print (current_external_folders)



    beta_version_extension_folder = filter(lambda x: "Published_Beta_Version"  in x, current_external_folders)
    stable_version_extension_folder = filter(lambda x: x not in beta_version_extension_folder, current_external_folders)
    print (beta_version_extension_folder)
    print (stable_version_extension_folder)




    enneadtab_stable_version_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published"
    enneadtab_beta_tester_version_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published_Beta_Version"
    enneadtab_game_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Misc"

    
    from EnneadTab.REVIT import REVIT_APPLICATION
    from EnneadTab import DATA_FILE, USER, NOTIFICATION, ENVIRONMENT, SPEAK, ERROR_HANDLE, FOLDER

    if not USER.IS_DEVELOPER:
            
        if USER.is_revit_beta_tester():
            if enneadtab_beta_tester_version_folder not in current_external_folders:
                current_external_folders.append(enneadtab_beta_tester_version_folder)
            if enneadtab_stable_version_folder in current_external_folders:
                current_external_folders.remove(enneadtab_stable_version_folder)
        else:
            if enneadtab_beta_tester_version_folder  in current_external_folders:
                current_external_folders.remove(enneadtab_beta_tester_version_folder)
            if enneadtab_stable_version_folder not in current_external_folders:
                current_external_folders.append(enneadtab_stable_version_folder)


    if include_game:
        if enneadtab_game_folder not in current_external_folders:
            current_external_folders.append(enneadtab_game_folder)
    else:
        if enneadtab_game_folder in current_external_folders:
            current_external_folders.remove(enneadtab_game_folder)
            
            
    user_config.set_thirdparty_ext_root_dirs(current_external_folders)
    from pyrevit.loader import sessionmgr
    sessionmgr.reload_pyrevit()
    return
    import pyrevitcore_globals
    execute_command(pyrevitcore_globals.PYREVIT_CORE_RELOAD_COMMAND_NAME)
    return


# Create a subclass of IExternalEventHandler
class SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.kwargs = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):
        try:
            try:
                #print "try to do event handler func"
                self.OUT = self.do_this(*self.kwargs)
            except Exception as e:
                print ("failed + " + str(e))
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"



# A simple WPF form used to call the ExternalEvent
class main_setting_UI(forms.WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.change_extension_event_handler = SimpleEventHandler(change_extension_folder)

        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.change_extension_event_handler)

        return


    def __init__(self):

        self.pre_actions()
        xaml_file_name = 'EnneadTab_Setting_UI.xaml'
        forms.WPFWindow.__init__(self, xaml_file_name)

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")

        self.set_image_source(self.logo_img, logo_file)
        self.Height = 800
        """
        if not USER.IS_DEVELOPER:
            self.reminder_level_setting.Visibility = System.Windows.Visibility.Collapsed
            #self.ribbon_tab_setting.Visibility = System.Windows.Visibility.Collapsed
        """

        self.load_setting()

        self.toggle_bt_is_beta_tester.IsChecked = USER.is_revit_beta_tester()
        if not self.toggle_bt_is_beta_tester.IsChecked:
            self.checkbox_tab_beta.Visibility = System.Windows.Visibility.Collapsed


      


        self.Show()


    @ERROR_HANDLE.try_catch_error()
    def load_setting(self):

        setting_file = FOLDER.get_EA_dump_folder_file('revit_ui_setting.json')
        if not os.path.exists(setting_file):
            DATA_FILE.set_data(dict(), setting_file)
            self.checkbox_tab_tailor.IsChecked = True
            self.checkbox_tab_library.IsChecked = True
            self.checkbox_tab_beta.IsChecked = True
            return


        data = DATA_FILE.read_json_as_dict(setting_file)
        for key, value in data.items():
            ui_obj = getattr(self, key, None)
            if not ui_obj:
                continue

            
            if "checkbox" in key or "toggle_bt" in key or "radio_bt" in key:
                setattr(ui_obj, "IsChecked", value)
            if "textbox" in key:
                setattr(ui_obj, "Text", str(value))

        self.toggle_bt_is_tab_color.IsChecked = TABS.get_doc_colorizer_state()

        self.update_UI()
            

    @ERROR_HANDLE.try_catch_error()
    def save_setting(self):
        setting_file = FOLDER.get_EA_dump_folder_file('revit_ui_setting.json')
        data = DATA_FILE.read_json_as_dict(setting_file)


        setting_list = ["checkbox_tab_tailor", 
                        "checkbox_tab_library", 
                        "checkbox_tab_beta", 
                        "checkbox_game",
                        "toggle_bt_is_talkie",
                        "radio_bt_popup_minimal",
                        "radio_bt_popup_standard",
                        "radio_bt_popup_full",
                        "textbox_sync_monitor_interval",
                        "radio_bt_sync_monitor_is_checking",
                        "radio_bt_sync_monitor_never",
                        "checkbox_email_sync_gap",
                        "checkbox_email_opening_warning_diff",
                        "checkbox_email_local_warning_diff",
                        "toggle_bt_is_duck_allowed",
                        "checkbox_is_dumb_duck"]
        for key in setting_list:
            ui_obj = getattr(self, key)
            if "checkbox" in key or "toggle_bt" in key or "radio_bt" in key:
                data[key] = getattr(ui_obj, "IsChecked")
            if "textbox" in key:
                data[key] = getattr(ui_obj, "Text")



        DATA_FILE.set_data(data, setting_file)

        self.update_TTS()


    @ERROR_HANDLE.try_catch_error()
    def send_duck_click(self, sender, args):
        EnneaDuck.quack()
 

    @ERROR_HANDLE.try_catch_error()
    def tab_setting_changed(self, sender, args):
        for tab in ribbon.get_current_ui():
            #print tab.name
            #continue
            """EnneadTab_Basic
            EnneadTab_Tailor
            EnneadTab_Advanced
            EnneadTab_Beta"""

            if tab.name == "Ennead Tailor":
                # not new state since the visible value is reverse
                tab.visible = self.checkbox_tab_tailor.IsChecked
            if tab.name == "Ennead Library":
                # not new state since the visible value is reverse
                tab.visible = self.checkbox_tab_library.IsChecked
            if tab.name == "Ennead Beta":
                # not new state since the visible value is reverse
                tab.visible = self.checkbox_tab_beta.IsChecked

    @ERROR_HANDLE.try_catch_error()
    def apply_setting_click(self, sender, args):
        self.save_setting()
        is_tester = self.toggle_bt_is_beta_tester.IsChecked
        is_game_included = self.checkbox_game.IsChecked
        
        from EnneadTab.REVIT import REVIT_APPLICATION
        from EnneadTab import DATA_FILE, USER, NOTIFICATION, ENVIRONMENT, SPEAK, ERROR_HANDLE, FOLDER
        USER.set_revit_beta_tester(is_tester)
        self.change_extension_event_handler.kwargs = is_tester, is_game_included
        self.ext_event.Raise()
        res = self.change_extension_event_handler.OUT
        self.Close()



    @ERROR_HANDLE.try_catch_error()
    def toggle_tab_color_click(self, sender, args):
        
        TABS.toggle_doc_colorizer()
        #self.toggle_bt_is_tab_color.IsChecked = not(self.toggle_bt_is_tab_color.IsChecked)

        """
        should also add function to display color legend for what current tabs color refer to what files
        """

    @ERROR_HANDLE.try_catch_error()
    def radio_bt_sync_monitor_click(self, sender, args):
        self.update_UI()

    @ERROR_HANDLE.try_catch_error()
    def update_UI(self):
        if  self.radio_bt_sync_monitor_is_checking.IsChecked:
            self.textbox_sync_monitor_interval.IsEnabled = True
            self.textbox_sync_monitor_interval.Background = System.Windows.Media.Brushes.White
        else:
            self.textbox_sync_monitor_interval.IsEnabled = False
            self.textbox_sync_monitor_interval.Background = System.Windows.Media.Brushes.Gray



    @ERROR_HANDLE.try_catch_error()
    def update_TTS(self):
        file_name = "EA_TALKIE_KILL.kill"
        
        # if self.toggle_bt_is_talkie.IsChecked: # True means it is enabled
        if FOLDER.is_file_exist_in_dump_folder(file_name):
            FOLDER.remove_file_from_dump_folder(file_name)
        SPEAK.speak("I am back! How are you doing?")

        # else:
        #     filepath = FOLDER.get_EA_dump_folder_file(file_name)
        #     with open(filepath, 'w') as f:
        #         f.write("Kill!")


    def handleclick(self, sender, args):
        print ("surface clicked")

    def close_click(self, sender, args):
        self.Close()
        self.save_setting()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()



@ERROR_HANDLE.try_catch_error()
def main():

    modeless_form = main_setting_UI()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
    
