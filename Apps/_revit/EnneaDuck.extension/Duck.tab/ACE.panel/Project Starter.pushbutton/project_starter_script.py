#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """A floating window that give you quick access to all kinds of function needed when a new project is starting.

+Default Workset Creation
+New Sheet Created From Excel
+Quick project info filling"""


__title__ = "Project\nInitiating"
__tip__ = True

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
from pyrevit import forms #
from pyrevit import script #


from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ENVIRONMENT, USER, NOTIFICATION, ENVIRONMENT_CONSTANTS, ERROR_HANDLE, EXCEL, FOLDER
import traceback
from Autodesk.Revit import DB # pyright: ignore 
import random
from Autodesk.Revit import UI # pyright: ignore
import System
import imp
import importlib
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True

import ENNEAD_LOG
import sys
import os


current_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_folder)
from module_func_create_levels import LevelDataGrid



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
            except:
                print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"



def get_moudle(module_name):
    
    folder = r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\ACE.panel\Project Starter.pushbutton"
    
    full_file_path = r"{}\{}.py".format(folder, module_name)
    if not  USER.is_SZ():
        full_file_path =  FOLDER.remap_filepath_to_folder(full_file_path)
        
    return imp.load_source(module_name, full_file_path)

# A simple WPF form used to call the ExternalEvent
class project_starter_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):

        self.func_list = [("module_func_excel_sheet","excel_sheet_creator"),
                     ("module_func_create_worksets","create_worksets"),
                     ("module_func_workshare","enable_workshare"),
                     ("module_func_proj_info","set_proj_info"),
                     ("module_func_create_levels","create_levels")]
        for func_data in self.func_list:
            module_name, func_name = func_data
            # module = __import__(module_name)
            try:
                module = importlib.import_module(module_name)
            except:
                module = get_moudle(module_name)
            setattr(self, "{}_event_handler".format(func_name), SimpleEventHandler(getattr(module, func_name)))
            setattr(self, "ext_event_{}".format(func_name), ExternalEvent.Create(getattr(self, "{}_event_handler".format(func_name))))
        
        

        return

    def __init__(self, doc):
        self.doc = doc
        self.pre_actions()

        xaml_file_name = r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\ACE.panel\Project Starter.pushbutton\project_starter_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        if not USER.is_SZ():
            xaml_file_name =  FOLDER.remap_filepath_to_folder(xaml_file_name)
            
            
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Project Initiator"

        self.sub_text.Text = "Some common function needed when you are about to start a new project."


        self.Title = "EnneadTab Project Initiator UI"

        if ENVIRONMENT_CONSTANTS.IS_LOCAL_OS:
            logo_file = "{}\logo_vertical_light.png".format(ENVIRONMENT_CONSTANTS.OS_CORE_IMAGES_FOLDER)
        else:
           
            logo_file = "{}\logo_vertical_light.png".format(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT)
        import os
        if not os.path.exists(logo_file):
            logo_file = "{}\logo_vertical_light_temp.png".format(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT) # note to self, remove this line so not to confuse later after IT fix peer link
        self.set_image_source(self.logo_img, logo_file)
       
   
        if not USER.is_SZ():
            self.tab_plans.Visibility = System.Windows.Visibility.Collapsed
            # )\nrepath default family to new project folder(Future)\n
            # pick shared parameter file(Future)\n
            # pick keynote file.(Future)"
            

        
        
        self.level_data_class = LevelDataGrid
        self.level_data_class.all_levels = [LevelDataGrid("Level 1", 6000)]
        self.level_data_grid.ItemsSource = self.level_data_class.all_levels
        
        
        self.Show()

    def get_handler_event_by_keyword(self, keyword):
        for func_data in self.func_list:
            module_name, func_name = func_data
            
            
            if keyword not in func_name:
                continue
                
            handler = getattr(self, "{}_event_handler".format(func_name))
            ext_event = getattr(self, "ext_event_{}".format(func_name))
            return handler, ext_event

    @ERROR_HANDLE.try_catch_error
    def create_workset_Click(self, sender, e):
            
        # # get all existing workset names
        # names = [ws.Name for ws in DB.FilteredWorksetCollector(doc) if ws.Kind == DB.WorksetKind.UserWorkset]
        # print names

        

        # return
        if not self.doc.IsWorkshared:
            NOTIFICATION.messenger (main_text = "This document is not workshared. Cannot Create Worksets.")
            return
        # A list of workset names
        default_workset_names = ['0_References', 
                                '0_Shared Levels & Grids', 
                                '1_Core', 
                                '1_FF&E', 
                                '1_Shell', 
                                '1_Interiors', 
                                '1_Site', 
                                '1_Structure',
                                '2_RVT Links', 
                                '3_CAD Links'] 
        selected_workset_names = forms.SelectFromList.show(default_workset_names,
                                                        title = "Select Ennead Standard Worksets To Add",
                                                        multiselect  = True)
        if not selected_workset_names:
            return
        
        
        handler, ext_event = self.get_handler_event_by_keyword("workset")
        handler.kwargs = self.doc, default_workset_names
        ext_event.Raise()
        res = handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"


    @ERROR_HANDLE.try_catch_error
    def create_sheet_from_excel_click(self, sender, e):
        # chaneg this to a path picker UI, also allow samepl excel to open
        # excel_path = forms.pick_excel_file(title="Where is the excel thjat has the new sheet data?")   
        excel_path = forms.pick_file(title="Where is the excel that has the new sheet data?",
                                     files_filter='Excel Workbook (*.xlsx)|*.xlsx|'
                                                '(If contain Chinese)Excel 97-2003 Workbook|*.xls')   

        if not excel_path:
            return
        # this is the sample excel for reference. 
        # excel_path = r"J:\2306\2_Record\2023-07-31 SD Submission\SD Sheetlist_REV00.xlsx"
        
        
        #  change this to a dropdown menu
        all_worksheet_names = EXCEL.get_all_worksheets(excel_path)
        worksheet_name = forms.SelectFromList.show(all_worksheet_names, multiselect = False, title = "Which worksheet contains the new sheet data?")
        if not worksheet_name:
            return
        
        def letter_to_index(letter):
            return ord(letter.lower()) - ord('a')
        
 
        
        data_map = {"sheet_number": letter_to_index(self.excel_header_sheet_number.Text),
                    "sheet_name": letter_to_index(self.excel_header_sheet_name.Text),
                    "translation":letter_to_index(self.excel_header_translation.Text),
                    "sheet_group": letter_to_index(self.excel_header_sheet_group_name.Text)}
        
        handler, ext_event = self.get_handler_event_by_keyword("excel")
        handler.kwargs = self.doc, excel_path, worksheet_name , data_map
        ext_event.Raise()
        res = handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"

    @ERROR_HANDLE.try_catch_error
    def open_sample_excel_click(self, sender, e):
        import module_func_excel_sheet
        module_func_excel_sheet.open_sample_excel()
        
        
    @ERROR_HANDLE.try_catch_error
    def enable_workshare_Click(self, sender, e):
        
        handler, ext_event = self.get_handler_event_by_keyword("workshare")
        is_cloud = self.raddial_bim360.IsChecked
        handler.kwargs = self.doc, is_cloud
        ext_event.Raise()
        res = handler.OUT
         

    @ERROR_HANDLE.try_catch_error
    def set_proj_para_Click(self, sender, e):
        handler, ext_event = self.get_handler_event_by_keyword("proj_info")
        data = {}
        data["Name"] = self.proj_info_proj_name.Text
        data["Number"] = self.proj_info_proj_number.Text
        data["ClientName"] = self.proj_info_client_name.Text
        data["BuildingName"] = self.proj_info_building_name.Text
        data["Address"] = self.proj_info_proj_address.Text
        
        data["FileName"] = self.proj_info_file_name.Text
        self.proj_info_file_name.Text = ""
        
        handler.kwargs = self.doc, data
        ext_event.Raise()
        res = handler.OUT
         
       

    @ERROR_HANDLE.try_catch_error
    def create_level_Click(self, sender, e):
        handler, ext_event = self.get_handler_event_by_keyword("create_levels")
       
        handler.kwargs = self.doc, self.level_data_grid.ItemsSource, self.tbox_building_prefix.Text
        ext_event.Raise()
        res = handler.OUT

    @ERROR_HANDLE.try_catch_error
    def level_data_add_Click(self, sender, e):
        # print sender
        # print (e)
        self.level_data_class.add_level(int(self.tbox_level_gap.Text))
        # print self.data_grid.all_levels
        self.update_data_grid()
        
    @ERROR_HANDLE.try_catch_error
    def level_data_remove_Click(self, sender, e):
        # print sender
        # print (e)
        self.level_data_class.remove_level()
        # print self.data_grid.all_levels
        self.update_data_grid()  
        
             
    def update_data_grid(self):
        
        self.level_data_grid.ItemsSource = sorted(self.level_data_class.all_levels, key = lambda x: x.level_elevation, reverse = True)
        
        # for x in self.level_data_grid.ItemsSource:
        #     print x.level_name
        #     print x.level_elevation
        
        
        pass
    
    
    @ERROR_HANDLE.try_catch_error
    def regenerate_level_Click(self, sender, e):
        self.level_data_class.all_levels = []
        for item in self.level_data_grid.ItemsSource[::-1]:
            try:
                level_gap = int(item.level_gap_formated)
            except:
                level_gap = item.level_gap
            self.level_data_class.all_levels.append(self.level_data_class(item.level_name,
                                                                          level_gap))
        
        self.level_data_class.format_display()
        self.update_data_grid()  
    
    
    @ERROR_HANDLE.try_catch_error
    def create_plan_Click(self, sender, e):
        NOTIFICATION.messenger (main_text =  "To be done: create plans.")

    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()




def project_starter(doc):
    modeless_form = project_starter_ModelessForm(doc)

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    try:
        project_starter(doc)
        ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
    except:
        print (traceback.format_exc())
