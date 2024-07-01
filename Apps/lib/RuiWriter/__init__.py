"""Run this in python 3.x
Do not use ironpython

Do not use any EnnadTab dependency"""


import os


import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
from IconHandler import IconHandler
from GuidHandler import GuidHandler
import MacroHandler as MH
import TabHandler as TH
import final_save as FS
import TabGroupHandler as TGH 
import MenuHandler as MH
import ButtonHandler as BH
from constants import MAIN_FOLDER, SPECIAL_LIST_KEY, DISTIBUTION_RUI, SELF_USE_RUI, INSTALLATION_RUI





class RuiWriter:
    

    def __init__(self) -> None:
        # self.main_data = OrderedDict()
        self.main_data = dict()

       

    def get_menu(self):
        for folder, _, files in os.walk(MAIN_FOLDER):
            if folder.endswith(".menu"):
                self.menu = MH.MenuHandler(folder)
                return self.menu.as_json()

    
    def get_tabs(self):
        return [tab.as_json() for tab in self.tabs]


    def get_marcos(self):
        macros = []
        for tab in self.tabs:
            # print (tab)
            for button in tab.buttons:
                if isinstance(button, BH.DividerHandler):
                    continue
                if button.macro_left:
                    macros.append(button.macro_left)
                if button.macro_right:
                    macros.append(button.macro_right)

        for button in self.menu.buttons:
            if button.macro_left:
                macros.append(button.macro_left)
     
        return [x.as_json() for x in macros]
                    
    def get_icons(self):
        icon_list = []
        for tab in self.tabs:
            icon_list.append(tab.icon)
            for button in tab.buttons:
                if isinstance(button, BH.DividerHandler):
                    continue
                if button.macro_left:
                    icon_list.append(button.macro_left.icon)
                if button.macro_right:
                    icon_list.append(button.macro_right.icon)

        for button in self.menu.buttons:
            if button.macro_left:
                icon_list.append(button.macro_left.icon)
                
        return IconHandler.chain_bitmap_text(icon_list)
       
    
    def assign_rui_basic(self):
        self.main_data["@major_ver"] = "3"
        self.main_data["@minor_ver"] = "0"
        self.main_data["@guid"] = GuidHandler("root").guid
        self.main_data["@localize"] = "False"
        self.main_data["@default_language_id"] = "1033"
        self.main_data["@dpi_scale"] = "100"
        self.main_data["extend_rhino_menus"] = {
            "menu": {
                "@guid": GuidHandler("extended_menu").guid,
                "text": {"locale_1033": "Extend Rhino Menus"}
            }
        }


    def get_toolbar_group_data(self):
        tab_groups = TGH.get_tabgroups(self.tabs)
        group_data = {
            "@guid": "fb209b37-3a90-4551-8c5e-36d544b2b5f6",
            "@dock_bar_guid32": "00000000-0000-0000-0000-000000000000",
            "@dock_bar_guid64": "83ae5f77-b8e0-43b4-8f99-5e06e0d15940",
            "@active_tool_bar_group": "a3a20efb-ebed-471b-9c1e-8790863dfc50",
            "@single_file": "False",
            "@hide_single_tab": "False",
            "@point_floating": "100,300",
            "text": {
                "locale_1033": "EnneadTab Dynamic Rui"
            }
            
        }

    

        
        group_data[SPECIAL_LIST_KEY] = [tab_group.as_json() for tab_group in tab_groups]
        group_data["dock_bar_info"] = {
                "@dpi_scale": "100",
                "@dock_bar": "False",
                "@docking": "True",
                "@horz": "False",
                "@visible": "True",
                "@floating": "False",
                "@mru_float_style": "8192",
                "@bar_id": "59522",
                "@mru_width": "868",
                "@point_pos": "57,0",
                "@float_point": "1454,694",
                "@rect_mru_dock_pos": "57,0,118,907",
                "@dock_location_u": "59420",
                "@dock_location": "right",
                "@float_size": "191,62"
            }
        
        return {"tool_bar_group": group_data}

    def run(self):

        GuidHandler.init_databease()
        
        # process folder to setup data tree
        self.setup_data()

        # save as rui as something new that can check and compare with real WIP
        self.save_to_rui()
        


        GuidHandler.update_database()



    def setup_data(self):
        self.assign_rui_basic()
        self.main_data["menus"] = self.get_menu()

        # assign e the logic once...
        self.tabs = TH.get_tabs()

        
        self.main_data["tool_bar_groups"] = self.get_toolbar_group_data()


        # tool bar item  =>> button
        # tool bar ==>  tab
        # tool bar group ==> the collection of tabs that you can dock

        # work order from tabs to button to macro to icon
        self.main_data["tool_bars"] = self.get_tabs()
        self.main_data["macros"] = self.get_marcos()

        self.main_data["bitmaps"] = self.get_icons()
        self.main_data["scripts"] = []
        
        # pprint.pprint(self.main_data, indent=2)


    def save_to_rui(self):

        for rui in [DISTIBUTION_RUI, SELF_USE_RUI, INSTALLATION_RUI]:
                
            FS.write_rui(self.main_data, rui)

            
        print("\n\n\n\nXML data has been saved to '.xml' as .rui.")

        # open this file in default program
        os.startfile(SELF_USE_RUI)


        # tried to use shutil copy but the copied rui is no longer reconigzed by RHino, so just creat it twice.
        # DISTIBUTION_RUI: no one should load it to avoid git conflict.and when uploaded to server foler, used for every one's 
        # initial installATION. tHE DISTRIBUTION still happen by hook open from developer
        # SELF_USE_RUI: can be laodded by developer computer
        
###################################################################



def run():
    RuiWriter().run()
###################################################################
if __name__ == "__main__":
    run()