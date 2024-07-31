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
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent # pyright: ignore 
from Autodesk.Revit.Exceptions import InvalidOperationException # pyright: ignore 


import System # pyright: ignore 



import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS
from EnneadTab import DATA_FILE, USER, NOTIFICATION, ENVIRONMENT, SPEAK, ERROR_HANDLE, FOLDER, IMAGE, LOG, DUCK, CONFIG


from pyrevit import script
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
    return
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




# A simple WPF form used to call the ExternalEvent
class MainSetting(REVIT_FORMS.EnneadTabModelessForm):

    def __init__(self, title, summery, xaml_file_name, **kwargs):
        self.Height = 800
        self.load_setting()
        super().__init__(title, summery, xaml_file_name, **kwargs)

    @ERROR_HANDLE.try_catch_error()
    def load_setting(self):
        data = DATA_FILE.get_data(CONFIG.GLOBAL_SETTING_FILE)
        for key, value in data.items():
            ui_obj = getattr(self, key, None)
            if not ui_obj:
                continue

            
            if "checkbox" in key or "toggle_bt" in key or "radio_bt" in key:
                setattr(ui_obj, "IsChecked", value)
            if "textbox" in key:
                setattr(ui_obj, "Text", str(value))

        # self.toggle_bt_is_tab_color.IsChecked = TABS.get_doc_colorizer_state()
        self.update_UI()
            

    @ERROR_HANDLE.try_catch_error()
    def save_setting(self):
        with DATA_FILE.update_data(CONFIG.GLOBAL_SETTING_FILE) as data:
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



        #  the handle of say or not is inside speak
        SPEAK.speak("I am back! How are you doing?")


    @ERROR_HANDLE.try_catch_error()
    def send_duck_click(self, sender, args):
        DUCK.quack()
 

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








    def handle_click(self, sender, args):
        print ("surface clicked")

    def close_click(self, sender, args):
        self.Close()
        self.save_setting()





@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    MainSetting(title = __title__, 
                summery = __doc__, 
                xaml_file_name = 'EnneadTab_Setting_UI.xaml', 
                external_funcs = [change_extension_folder])


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
    
