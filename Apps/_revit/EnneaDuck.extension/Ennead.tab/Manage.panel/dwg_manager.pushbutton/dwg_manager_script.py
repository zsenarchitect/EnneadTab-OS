#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """A floating window that help you manage DWG in the files. 
You can find, select, zoom any dwgs with detailed infor on creator, view association, hidden status, workset, file path and file size. 

For linked dwgs, you might also open file directly, open folder directly, and repath links to a selected folder."""


__title__ = "DWG\nManager"
__tip__ = True
import os
import math
import random
import traceback
import System

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from System import EventHandler, Uri


from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import _HostApplication
from pyrevit import HOST_APP

import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_APPLICATION
from EnneadTab import EXE, NOTIFICATION, IMAGE, ERROR_HANDLE, FOLDER
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True





def get_dwgs():

    dwgs_list = DB.FilteredElementCollector(doc).OfClass(DB.ImportInstance).WhereElementIsNotElementType().ToElements()
    list(dwgs_list).sort(key = lambda x: x.LookupParameter("Name"), reverse = True)
    return dwgs_list


@ERROR_HANDLE.try_catch_error()
def repath_all_dwgs(new_folder, dwg_type_list):

    t = DB.Transaction(doc, "Repath All Linked Dwgs")
    t.Start()
    for dwg_type in dwg_type_list:
        try:
            file_ref = dwg_type.GetExternalFileReference ()
            file_path = file_ref.GetPath()

            file_path = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(file_path)
            new_path = FOLDER.copy_file_to_folder(file_path, new_folder)
            dwg_type.LoadFrom(new_path)
        except Exception as e:
            print("Skip this dwg: {}\nBecasue: {}\n\n".format( dwg_type.LookupParameter("Type Name").AsString() , e ))
            continue
    t.Commit()




# Create a subclass of IExternalEventHandler
class dwg_manage_SimpleEventHandler(IExternalEventHandler):
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

def get_filesize(filepath, return_bytes = False):

    try:
        size_bytes = int(os.path.getsize(filepath))
    except:
        return "N/A"
    if return_bytes:
        return size_bytes

    if size_bytes == -1:
        return "N/A"
    size_unit = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    size = round(size_bytes / p, 2)
    return "{}{}".format(size, size_unit[i])

def get_dwg_file_path(dwg):
    
    dwg_type = doc.GetElement(dwg.GetTypeId ())
    try:
        file_ref = dwg_type.GetExternalFileReference ()
    except Exception as e:
        # print (dwg)
        # print(dwg_type)
        return "{}. Is this a cloud address?".format(e)
    file_path = file_ref.GetPath()
    file_path = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(file_path)
    return file_path


    return
    dwgs_list = DB.FilteredElementCollector(revit.doc).OfClass(DB.CADLinkType ).ToElements()
    for dwg in dwgs_list:
        if dwg.LookupParameter("Type Name").AsString() in dwg_name:
            pass
        try:
            file_ref = dwg.GetExternalFileReference ()
        except Exception as e:
            print (e)
            print 
            continue

class data_grid_obj:
    def __init__(self, dwg):
        self.dwg = dwg
        self.format_name = dwg.LookupParameter("Name").AsString()
        self.creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, dwg.Id).Creator

        if dwg.IsLinked:

            self.file_path = get_dwg_file_path(dwg)
            self.file_size = get_filesize(self.file_path, return_bytes = True)
            self.file_size_format = get_filesize(self.file_path, return_bytes = False)
            self.dwg_kind = "Linked"
        else:
            self.file_path = "N/A"
            self.file_size = "N/A"
            self.file_size_format = "N/A"
            self.dwg_kind = "Imported"


        if dwg.ViewSpecific:
            self.dwg_type = "2D"
            self.view = doc.GetElement(dwg.OwnerViewId)
            self.view_name = self.view.Name
            self.is_hidden = "Hidden" if dwg.IsHidden(self.view) else ""
            self.workset = "N/A"
        else:
            self.dwg_type = "3D"
            self.view = None
            self.view_name = "N/A"
            self.is_hidden = "N/A"
            self.workset = doc.GetWorksetTable().GetWorkset(dwg.WorksetId).Name



# A simple WPF form used to call the ExternalEvent
class dwg_manage_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.simple_event_handler = dwg_manage_SimpleEventHandler(repath_all_dwgs)

        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.simple_event_handler)
        #print "preaction done"
        #print self.simple_event_handler
        #print self.simple_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return


    @ERROR_HANDLE.try_catch_error()
    def __init__(self):
        self.pre_actions()
        xaml_file_name = "dwg_manager_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab DWG Manager"

        self.sub_text.Text = "Manage your dwgs in this form."


        self.Title = "EnneadTab DWG Manager UI"

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)


        #get all dwgs in project
        all_dwgs = get_dwgs()

        if len(all_dwgs) == 0:
            self.sub_text.Text = "There is no dwgs in the project to manage."
        else:
            #check if it is linked
            self.dwgs_imported = []
            self.dwgs_linked = []
            for dwg in all_dwgs:
                if dwg.IsLinked:
                    self.dwgs_linked.append(dwg)
                else:
                    self.dwgs_imported.append(dwg)

            self.init_data_grid()

        self.Show()

    @ERROR_HANDLE.try_catch_error()
    def init_data_grid(self):

        def good_dwg(dwg):
            if not self.checkbox_3d_dwg.IsChecked:
                if not dwg.ViewSpecific:
                    return False
            if not self.checkbox_2d_dwg.IsChecked:
                if  dwg.ViewSpecific:
                    return False

            if not self.checkbox_linked_dwg.IsChecked:
                if  dwg.IsLinked:
                    return False

            if not self.checkbox_imported_dwg.IsChecked:
                if not dwg.IsLinked:
                    return False

            return True

        # self.main_data_grid.Columns.Clear()
        # self.main_data_grid.Columns.Add(DataGridTextColumn(Header = "Name", Binding = Binding("format_name")))
        # self.main_data_grid.Columns.Add(DataGridTextColumn(Header = "Creator", Binding = Binding("creator")))
        # self.main_data_grid.Columns.Add(DataGridTextColumn(Header = "File Path", Binding = Binding("file_path")))
        self.main_data_grid.ItemsSource = [data_grid_obj(dwg) for dwg in self.dwgs_linked+self.dwgs_imported if good_dwg(dwg)]
        

    @ERROR_HANDLE.try_catch_error()
    def preview_selection_changed(self, sender, args):
        obj = self.main_data_grid.SelectedItem
        if not obj:
            self.textblock_dwg_detail.Text = ""
            return

        self.textblock_dwg_detail.Text = obj.format_name
        self.textblock_dwg_detail.Text += "\nCreated By: [{}]".format( obj.creator)
        self.textblock_dwg_detail.Text += "\nDWG Kind: " + obj.dwg_kind
        self.textblock_dwg_detail.Text += "\nDWG Type: " + obj.dwg_type
        if obj.dwg_type == "2D":
            self.textblock_dwg_detail.Text += "\nView Name: " + obj.view_name
            self.bt_open_view.Visibility = System.Windows.Visibility.Visible
            if obj.is_hidden == "Hidden":
                self.textblock_dwg_detail.Text += "\nIs Hidden in this view."
        else:
            self.textblock_dwg_detail.Text += "\nWorkset: " + obj.workset
            self.bt_open_view.Visibility = System.Windows.Visibility.Hidden
            
        if obj.dwg_kind == "Linked":
            self.textblock_dwg_detail.Text += "\nLinked DWG: "
            self.textblock_dwg_detail.Text += "\nFile Path: " + obj.file_path
            self.textblock_dwg_detail.Text += "\nFile Size: " + obj.file_size_format
            self.bt_open_dwg.Visibility = System.Windows.Visibility.Visible
            self.bt_open_dwg_folder.Visibility = System.Windows.Visibility.Visible
        else:
            self.textblock_dwg_detail.Text += "\n\nImported DWG. Please consider replaced to linked DWG. "
            self.bt_open_dwg.Visibility = System.Windows.Visibility.Hidden
            self.bt_open_dwg_folder.Visibility = System.Windows.Visibility.Hidden

    @ERROR_HANDLE.try_catch_error()
    def generic_click(self, is_V):
        #print "Clicking " + keyword
        if not self.ref_tag:
            self.debug_textbox.Text = "There is no ref tag captured."
            return


        self.simple_event_handler.kwargs = self.ref_tag, self.bad_tags, is_V
        self.ext_event.Raise()
        res = self.simple_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"


    @ERROR_HANDLE.try_catch_error()
    def select_dwg_click(self, sender, args):
        obj = self.main_data_grid.SelectedItem
        if not obj:
            return
        REVIT_SELECTION.set_selection(obj.dwg)


    @ERROR_HANDLE.try_catch_error()
    def zoom_dwg_click(self, sender, args):
        obj = self.main_data_grid.SelectedItem
        if not obj:
            return
        REVIT_SELECTION.zoom_selection(obj.dwg) 

    @ERROR_HANDLE.try_catch_error()
    def open_view_click(self, sender, args):
        obj = self.main_data_grid.SelectedItem
        if not obj:
            return
        if not obj.view:
            return

        uidoc.ActiveView = obj.view




    @ERROR_HANDLE.try_catch_error()
    def open_dwg_click(self, sender, args):
        obj = self.main_data_grid.SelectedItem
        if not obj:
            return

        if obj.file_path == "N/A":
            self.debug_textbox.Text = "This DWG has noth file path."
            return

        if not os.path.exists(obj.file_path):
            self.debug_textbox.Text = "This DWG file path does not exist."
            NOTIFICATION.messenger("This dwg path is not valid.")
            return
        EXE.try_open_app(obj.file_path)




    @ERROR_HANDLE.try_catch_error()
    def open_dwg_folder_click(self, sender, args):
        obj = self.main_data_grid.SelectedItem
        if not obj:
            return
        if obj.file_path == "N/A":
            return
        dwg_folder = os.path.dirname(obj.file_path)
        os.startfile(dwg_folder)


    @ERROR_HANDLE.try_catch_error()
    def repath_dwgs_click(self, sender, args):
        

        dwg_type_list = DB.FilteredElementCollector(doc).OfClass(DB.CADLinkType ).ToElements()

        new_folder = forms.pick_folder(title = "Select a new folder to copy DWGs to")
        if not new_folder:
            self.debug_textbox.Text = "No Folder Selected."
            return

        if len(dwg_type_list) == 0:
            self.debug_textbox.Text = "There is no DWG in this project."
            
            return


        self.simple_event_handler.kwargs = new_folder, dwg_type_list
        self.ext_event.Raise()
        res = self.simple_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"


        self.Close()


    @ERROR_HANDLE.try_catch_error()
    def setting_changed(self, sender, args):
        self.init_data_grid()
        return
        #print "setting changed"
        if self.checkbox_3d_dwg.IsChecked:
            self.main_data_grid.ItemsSource = [x for x in self.main_data_grid.ItemsSource if x.dwg_type == "3D"]
        if self.checkbox_3d_dwg.IsChecked:
            self.main_data_grid.ItemsSource = [x for x in self.main_data_grid.ItemsSource if x.dwg_type == "2D"]

        if self.checkbox_linked_dwg.IsChecked:
            self.main_data_grid.ItemsSource = [x for x in self.main_data_grid.ItemsSource if x.dwg_kind == "Linked"]

        if self.checkbox_imported_dwg.IsChecked:
            self.main_data_grid.ItemsSource = [x for x in self.main_data_grid.ItemsSource if x.dwg_kind == "Imported"]


    @ERROR_HANDLE.try_catch_error()
    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()
    

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()






################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    try:

        modeless_form = dwg_manage_ModelessForm()
     
    except:
        print (traceback.format_exc())
