#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "A floating window that give you quick access to review un-sheeted views, ranked by creator, view group, view type and more. View name can be prefixed to make it more informative the author even from project broswer.\n\n The review process can be quick becasue the view have been exported as jpgs and reviewed quickly. You can also directly open actual view, or delete view in the same window after reviewing.\n\nIf you want to limit how much to see, you can show only views from you."
__title__ = "Manage\nWorking Views"
__tip__ = True

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import os
import time


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_APPLICATION
from EnneadTab import USER, NOTIFICATION, DATA_CONVERSION, IMAGE, ERROR_HANDLE, FOLDER
import traceback
from Autodesk.Revit import DB # pyright: ignore 
import random
from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True





@ERROR_HANDLE.try_catch_error()
def delete_views(view):

    t = DB.Transaction(doc, "Delete Views")
    t.Start()
    is_success = True
    try:
        print ("Delete view: {}".format(view.Name))
        doc.Delete(view.Id)
    except Exception as e:
        print ("Cannot delete view.")
        is_success = False
    t.Commit()

    return is_success



@ERROR_HANDLE.try_catch_error()
def modify_creator_in_view_name(views, is_adding_creator):
    views = REVIT_SELECTION.filter_elements_changable(views)

    t = DB.Transaction(doc, "Rename Views")
    t.Start()
    for view in views:
        if not view:
            continue
        if "{" in view.Name:
            continue
        if "enneadtab" in view.Name.lower():
            continue
        creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, view.Id).Creator
        simple_creator = creator.split("@")[0] if "@" in creator else creator


        ########################################################
        FORMAT_KEY = "____("# 4 underscore and ()
        FORMAT_FULL_SURFIX = FORMAT_KEY + simple_creator + ")"
        ########################################################
        
        if is_adding_creator:
            # skip view that alrady in new format
            if FORMAT_KEY in view.Name:
                continue

            # this is 2nd version also retiring
            if "____from(" in view.Name:
                temp_name = "{}____({})".format(view.Name.split("____from(")[0], simple_creator)
                count = 0
                while count < 5:
                    try:
                        view.Name = temp_name
                        break
                    except:
                        temp_name += "_new"
                        count += 1
                continue

            # handle 1st old format, first return the old format to raw name then directly assign new name
            if "_from(" in view.Name:
                temp_name = "{}____from({})".format(view.Name.split("_from(")[0], simple_creator)
                count = 0
                while count < 5:
                    try:
                        view.Name = temp_name
                        break
                    except:
                        temp_name += "_new"
                        count += 1
                continue

            new_name = view.Name + FORMAT_FULL_SURFIX

            try:
                view.Name = new_name
            except Exception as e:
                print ("Cannot modify view name for <{}> becasue {}".format(output.linkify(view.Id, title = view.Name), e))


        else:# removing creator from view name

            # #handle 1st old format
            # if "_from(" not in view.Name:
            #     continue

            # #handle 2nd format
            # if "____from(" not in view.Name:
            #     continue

            # # handle current format
            # if FORMAT_KEY not in view.Name:
            #     continue

            # print FORMAT_FULL_SURFIX


            found_flag = False
            if "_from({})".format(creator) in view.Name:
                new_name = view.Name.replace("_from({})".format(creator), "")
                found_flag = True
            if "____from({})".format(simple_creator) in view.Name:
                new_name = view.Name.replace("____from({})".format(simple_creator), "")
                found_flag = True
            if FORMAT_FULL_SURFIX in view.Name:
                new_name = view.Name.replace(FORMAT_FULL_SURFIX, "")
                found_flag = True

            if not found_flag:
                continue

            count = 0
            while count < 5:
                try:
                    view.Name = new_name.rstrip("_")
                    break
                except:
                    new_name += "_new"
                    count += 1
    t.Commit()

    return


# Create a subclass of IExternalEventHandler
class delete_view_SimpleEventHandler(IExternalEventHandler):
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

def is_no_sheet(view):
    if "{" in view.Name:
        return False
    if str(view.ViewType) in [ "Legend", "Schedule", "SystemBrowser", "ProjectBrowser", "DrawingSheet"]:
        return False
    if "revision" in view.Name.lower():
        return False
    if "schedule" in view.Name.lower():
        return False
    if view.IsTemplate:
        return False
    if view.LookupParameter("Sheet Number") is None:
        return True
    if view.LookupParameter("Sheet Number").AsString() == "---":
        return True
    return False

class DataGrid_Preview_Obj(object):



    def __init__(self, view):
        self.view = view
        self.format_name = view.Name
        self.view_type = view.ViewType.ToString()
        self.creator = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, view.Id).Creator

        self.organization_list = ["Views_$Group", "Views_$Series"]
        for x in self.organization_list:
            if view.LookupParameter(x):
                value = view.LookupParameter(x).AsString()

            else:
                value = "N/A"
            setattr(self, x.replace("$", ""),  value)



# A simple WPF form used to call the ExternalEvent
class manage_working_view_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.delete_view_event_handler = delete_view_SimpleEventHandler(delete_views)
        self.ext_event_delete_view = ExternalEvent.Create(self.delete_view_event_handler)


        self.add_creator_event_handler = delete_view_SimpleEventHandler(modify_creator_in_view_name)
        self.ext_event_add_creator = ExternalEvent.Create(self.add_creator_event_handler)
        return

    def __init__(self):
        self.pre_actions()

        xaml_file_name = "manage_working_view_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Manage Working Views"

        self.sub_text.Text = "Use this window to help find non-hseet view that was created by you, and decide if want to delete them from project."


        self.Title = "EnneadTab Manage Working Views"

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.set_image_source(self.monitor_icon, "monitor_icon.png")
        self.set_image_source(self.preview_image, "DEFAULT PREVIEW_CANNOT FIND PREVIEW IMAGE.png")
        self.set_image_source(self.status_icon, "update_icon.png")



        self.output_folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Work_View_Collection\{}".format("UnSheeted Views Jpgs for [{}]".format(doc.Title))



        self.data_grid.ItemsSource = [DataGrid_Preview_Obj(x) for x in self.get_non_sheet_views()]




        self.Show()

    def get_non_sheet_views(self, is_me_only = False):



        views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
        no_sheet_views = filter(is_no_sheet, views)
        no_sheet_views.sort(key = lambda x:x.Name)
        if is_me_only:
            no_sheet_views = filter(lambda x: DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, x.Id).Creator == USER.get_autodesk_user_name(), no_sheet_views)
        return no_sheet_views

    @ERROR_HANDLE.try_catch_error()
    def export_working_views_Click(self, sender, e):
        will_close = REVIT_APPLICATION.do_you_want_to_sync_and_close_after_done()
        total = len(self.data_grid.ItemsSource)
        for i, preview_obj in enumerate(self.data_grid.ItemsSource):
            self.debug_textbox.Text = "{}/{}".format(i + 1, total)
            preview_image = self.export_image_from_view( preview_obj.view, doc)
            try:
                self.set_image_source(self.preview_image, preview_image)
            except:
                self.set_image_source(self.preview_image, "DEFAULT PREVIEW_CANNOT FIND PREVIEW IMAGE.png")


        print ("\n\n Export preview finished.")
        self.debug_textbox.Text = "{} preview updated.".format( total)
        if will_close:
            self.Close()
            REVIT_APPLICATION.sync_and_close()
            



    @ERROR_HANDLE.try_catch_error()
    def preview_selection_changed(self, sender, e):
        if len(self.data_grid.ItemsSource) == 0:
            return

        obj = self.data_grid.SelectedItem

        try:
            #preview_image = "{}\{}.jpg".format(self.output_folder, obj.view.UniqueId)
            preview_image = self.get_true_preview_image(obj.view.UniqueId)
            self.set_image_source(self.preview_image, preview_image)

            creation_time = time.ctime(os.path.getctime(preview_image))
            note = "{}\nCreated By: {}\nPreview Generated: {}".format(obj.format_name, obj.creator, creation_time)
            self.textblock_export_status.Text = note
        except:
            self.update_preview_grid()
            self.set_image_source(self.preview_image, "DEFAULT PREVIEW_CANNOT FIND PREVIEW IMAGE.png")
            self.textblock_export_status.Text = ""

    @ERROR_HANDLE.try_catch_error()
    def UI_changed(self, sender, e):
        self.update_preview_grid()

    @ERROR_HANDLE.try_catch_error()
    def refresh_table_Click(self, sender, e):
        self.update_preview_grid()
        self.debug_textbox.Text = "Currently showing {} views.".format(len(self.data_grid.ItemsSource))

    @ERROR_HANDLE.try_catch_error()
    def update_preview_grid(self):
        is_me_only = self.checkbox_me_only.IsChecked
        self.data_grid.ItemsSource = [DataGrid_Preview_Obj(x) for x in self.get_non_sheet_views(is_me_only)]
        pass

    @ERROR_HANDLE.try_catch_error()
    def open_view_click(self, sender, e):
        obj = self.data_grid.SelectedItem
        if not obj:
            return
        if not obj.view:
            self.update_preview_grid()
            return
        uidoc.ActiveView = obj.view
        pass

    @ERROR_HANDLE.try_catch_error()
    def delete_view_click(self, sender, e):
        obj = self.data_grid.SelectedItem
        if not obj:
            return

        # need to save the id so later after view is removed and grid data regenerate, i can still delete freom folder
        this_view_id = obj.view.UniqueId

        self.delete_view_event_handler.kwargs = obj.view,
        self.ext_event_delete_view.Raise()
        res = self.delete_view_event_handler.OUT


        #preview_image = "{}\{}.jpg".format(self.output_folder, this_view_id)
        preview_image = self.get_true_preview_image(this_view_id)
        if os.path.exists(preview_image):
            os.remove(preview_image)
        self.update_preview_grid()


    def get_true_preview_image(self, unique_id):
        for file in os.listdir(self.output_folder):
            if unique_id in file:
                break
        preview_image = "{}\{}".format(self.output_folder, file)
        return preview_image

    @ERROR_HANDLE.try_catch_error()
    def append_creator_name_click(self, sender, e):
        self.view_name_change(is_adding_creator = True)


    @ERROR_HANDLE.try_catch_error()
    def remove_creator_name_click(self, sender, e):
        self.view_name_change(is_adding_creator = False)


    def view_name_change(self, is_adding_creator):
        if len(self.data_grid.ItemsSource) == 0:
            return

        self.add_creator_event_handler.kwargs = [x.view for x in self.data_grid.ItemsSource], is_adding_creator
        self.ext_event_add_creator.Raise()
        res = self.add_creator_event_handler.OUT
        self.update_preview_grid()





    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()



    def export_image_from_view(self, view, doc):

        print ("-----")


        time_start = time.time()

        file_name = view.UniqueId


        print ("preparing [{}].jpg".format(file_name))

        output_folder = self.output_folder
     

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)


        opts = DB.ImageExportOptions()
        opts.FilePath = FOLDER.get_EA_dump_folder_file('{}.jpg'.format(file_name))
        if os.path.exists(opts.FilePath):
            os.remove(opts.FilePath)
        opts.ImageResolution = DB.ImageResolution.DPI_300
        opts.ExportRange = DB.ExportRange.SetOfViews
        opts.ZoomType = DB.ZoomFitType.FitToPage
        opts.PixelSize = 3000
        opts.SetViewsAndSheets(DATA_CONVERSION.list_to_system_list([view.Id]))

        attempt = 0

        while True:
            try:
                doc.ExportImage(opts)
                break
            except:
                print ("retry printing " + str(view.Name))
                time.sleep(1.5)
                attempt += 1
            if attempt == 5:
                break

        print( "Image export succesfully")

        time_end = time.time()
        #cleanup_jpg_name()
        print ("view to Jpg takes {} seconds".format( time_end - time_start))

        #add_to_log(file_name + ".jpg", time_end - time_start)
        NOTIFICATION.toast(app_name = "EnneadTab Exporter",
                                main_text = "[{}.jpg] saved.".format(view.Name))

        """clean jpg name"""
        file_names = os.listdir(FOLDER.get_EA_local_dump_folder())
        desired_name = file_name

        for file_name in file_names:
            if desired_name in file_name and ".jpg" in file_name.lower():
                try:
                    # os.path.join(output_folder, file_name)
                    os.rename("{}\{}".format(FOLDER.get_EA_local_dump_folder(), file_name),os.path.join(FOLDER.get_EA_local_dump_folder(), desired_name + ".jpg"))
                except Exception as e:
                    print ("skip {} becasue: {}".format(file_name, e))


        final_path = FOLDER.copy_file_to_folder(opts.FilePath, output_folder)
        os.remove(opts.FilePath)
        return final_path



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    try:
        modeless_form = manage_working_view_ModelessForm()
    except:
        print (traceback.format_exc())
