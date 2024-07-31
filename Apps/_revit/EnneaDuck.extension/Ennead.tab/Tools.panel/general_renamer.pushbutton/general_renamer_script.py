#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """A floating window that give you quick access to all kinds of renamer function.
    - Add/Remove a prefix for selected views.
    - Change Views/SHeets to upper case.
    - Format view names based on detail number and sheet number.
    - Rename family on spot without going thru the project broswer."""
__title__ = "Super\nRenamer"
__tip__ = True

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent # pyright: ignore 
from Autodesk.Revit.Exceptions import InvalidOperationException # pyright: ignore 
from pyrevit.forms import WPFWindow
from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import IMAGE, USER, NOTIFICATION, ERROR_HANDLE, LOG
import traceback
from Autodesk.Revit import DB # pyright: ignore 
import random
from Autodesk.Revit import UI # pyright: ignore
import System # pyright: ignore 
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True




@ERROR_HANDLE.try_catch_error()
def view_prefix_modifier(is_adding_prefix, prefix ):
    views = forms.select_views(title="Select views to modify",
                               use_selection=True)
    if not views:
        return


    
    t = DB.Transaction(doc, "Prefix View Name")
    t.Start()
    for view in views:
        if is_adding_prefix:
            view.Name = prefix + view.Name
        else:
            view.Name = view.Name.replace(prefix, "")
    t.Commit()
    NOTIFICATION.messenger (main_text = "All views name prefix modified!")

@ERROR_HANDLE.try_catch_error()
def all_cap_view_name(will_cap_sheet, will_cap_view):
    t = DB.Transaction(doc, "Cap View/Sheet Names")
    t.Start()
    for sheet in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements():
        # make sheet name upper case
        if will_cap_sheet:
            sheet.Name = sheet.Name.upper()
            
        if will_cap_view:
            for viewId in sheet.GetAllPlacedViews():
                view = doc.GetElement(viewId)
                view.Name = view.Name.upper()

    t.Commit()
    NOTIFICATION.messenger (main_text = "All views/sheets name reformated!")


@ERROR_HANDLE.try_catch_error()
def all_cap_spatial_element_name(will_cap_room, will_cap_area):
    t = DB.Transaction(doc, "Cap Rooms and Areas")
    t.Start()
    if will_cap_room:
        for room in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements():
        # make sheet name upper case
        
            room.LookupParameter("Name"). Set(room.LookupParameter("Name").AsString().upper())
            
    if will_cap_area:
        for area in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements():
        # make sheet name upper case
        
            area.LookupParameter("Name"). Set(area.LookupParameter("Name").AsString().upper())
          

    t.Commit()
    NOTIFICATION.messenger (main_text = "All Rooms and Areas name reformated!")

    
def remove_creator_mark(name):
    if "_from" in name:
        name = name.split("_from")[0]

    if "____from" in name:
        name = name.split("____from")[0]

    return name

@ERROR_HANDLE.try_catch_error()
def rename_views(doc, sheets, is_default_format, is_original_flavor, attempt = 0, show_log = True):

    if attempt > 3:
        return

    t = DB.Transaction(doc, "Rename Views")
    if not t.HasStarted():
        t.Start()

    failed_sheets = set()
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    def is_user_view(view):
        if view.IsTemplate:
            return False
        if view.ViewType.ToString() in ["Legend", "Schedule"]:
            return False
        return True
    all_views = filter(lambda x: is_user_view(x), all_views)

    view_names_pool = [x.Name for x in all_views]


    for sheet in sheets:
        sheet_num = sheet.SheetNumber

        is_only_one_view = len(list(sheet.GetAllPlacedViews())) == 1

        #for view on current sheet
        for view_id in sheet.GetAllPlacedViews():
            view = doc.GetElement(view_id)

            para = view.LookupParameter("Exclude Renaming")
            if para and para.AsInteger() == 1:
                continue

            if doc.IsWorkshared:
                current_owner = view.LookupParameter("Edited by").AsString()
                if current_owner != "" and current_owner != USER.get_autodesk_user_name():
                    if show_log:
                        print( "Skip view owned by {}. View Name = {}".format(current_owner, view.Name))
                    continue



            if view.ViewType.ToString() in ["Legend", "Schedule"]:
                continue

            #print revit.doc.GetElement(view.ViewId).Name
            if "{3D" in view.Name:
                continue


            refill_title = False
            detail_num_para_id = DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
            if is_only_one_view:
                view.Parameter[detail_num_para_id].Set("10")
            detail_num = view.Parameter[detail_num_para_id].AsString() #get view detail num

                

            title_para_id = DB.BuiltInParameter.VIEW_DESCRIPTION
            original_title = view.Parameter[title_para_id].AsString() #get view title

            name_para_id = DB.BuiltInParameter.VIEW_NAME
            original_name = view.Parameter[name_para_id].AsString() #get view name,if none, then use view name


            if not(original_title):
                new_title = original_name
                refill_title = True
            else:
                new_title = original_title


            new_title = remove_creator_mark(new_title)

            if is_default_format:
                new_view_name = str(sheet_num) + "_" + str(detail_num) + "_" + str(new_title)
            else:
                new_view_name = str(detail_num) + "_" + str(sheet_num) + "_" + str(new_title)
            #forms.alert(str(new_view_name))


            new_view_name = remove_creator_mark(new_view_name)

            if new_view_name == view.Name and new_title == original_title:
                #print "Skip {}".format(new_view_name)
                continue

            if new_view_name in view_names_pool:
                #print new_view_name
                failed_sheets.add(sheet)
                if show_log:
                    print ("Will try to visit <{}> again to avoid using same name.".format(view.Name))
                view.Parameter[name_para_id].Set(new_view_name + "_Pending")
                #print view
                continue

            if is_original_flavor:
                try:
                    if str(sheet_num) + "_" + str(detail_num) + "_" in new_view_name:
                        native_view_name = new_view_name.replace(str(sheet_num) + "_" + str(detail_num) + "_" , "")
                    if str(detail_num) + "_" + str(sheet_num) + "_" in new_view_name:
                        native_view_name = new_view_name.replace(str(detail_num) + "_" + str(sheet_num) + "_" , "")

                    while native_view_name in view_names_pool:
                        native_view_name = native_view_name + "_OverlappingViewName"
                    print ("{}-->{}".format(new_view_name, native_view_name))
                    view.Parameter[title_para_id].Set(new_title)
                    view.Parameter[name_para_id].Set(native_view_name)
                    view_names_pool.append(native_view_name)
                except Exception as e:
                    if show_log:
                        print ("Skip {} becasue {}".format(view.Name, e))
            else:
                try:
                    
                    view.Parameter[title_para_id].Set(new_title)
                    view.Parameter[name_para_id].Set(new_view_name)
                except:
                    if show_log:
                        print ("Skip {}".format(view.Name))
               

    if len(list(failed_sheets)) > 0:
        attempt += 1
        if show_log:
            print ("\n\nAttemp = {}".format(attempt))
       
        rename_views(doc, list(failed_sheets), is_default_format, is_original_flavor, attempt, show_log)

    if not t.HasEnded():
        t.Commit()

@ERROR_HANDLE.try_catch_error()
def rename_family(selected_element):
    current_family_name = selected_element.Symbol.Family.Name
    t = DB.Transaction(doc, "Rename Views")
    t.Start()
    try:
        new_family_name = forms.ask_for_string(default= current_family_name, \
                                                prompt="What is the new name?", \
                                                title="Family Name change", \
                                                width = 1500)

        if new_family_name == current_family_name:
            t.RollBack()
            return

        if new_family_name == "":
            t.RollBack()
            return

        if current_family_name != new_family_name:
            selected_element.Symbol.Family.Name = new_family_name
            t.Commit()
            return


    except Exception as e:
        print (e)
        REVIT_FORMS.notification(main_text = "This name taken, try again.")
        t.RollBack()
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
            except:
                print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"





# A simple WPF form used to call the ExternalEvent
class SuperRenamer(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.rename_view_event_handler = SimpleEventHandler(rename_views)
        self.ext_event_rename_view = ExternalEvent.Create(self.rename_view_event_handler)


        self.rename_family_event_handler = SimpleEventHandler(rename_family)
        self.ext_event_rename_family = ExternalEvent.Create(self.rename_family_event_handler)
        #print "preaction done"
        #print self.rename_view_event_handler
        #print self.rename_view_event_handler.kwargs
        #print self.ext_event_rename_view
        #print "-------"
        self.all_cap_view_event_handler = SimpleEventHandler(all_cap_view_name)
        self.ext_event_all_cap_view_name = ExternalEvent.Create(self.all_cap_view_event_handler)

        self.all_cap_spatical_element_event_handler = SimpleEventHandler(all_cap_spatial_element_name)
        self.ext_event_all_cap_spatial_element_name = ExternalEvent.Create(self.all_cap_spatical_element_event_handler)

        self.view_prefix_modifier_event_handler = SimpleEventHandler(view_prefix_modifier)
        self.ext_event_view_prefix_modifier = ExternalEvent.Create(self.view_prefix_modifier_event_handler)

        return

    def __init__(self):
        self.pre_actions()

        xaml_file_name = "SuperRenamer.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Super Renamer"

        self.sub_text.Text = "Some common renaming function."


        self.Title = "EnneadTab Renamer UI"

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.set_image_source(self.sample_img_project_browser, "sample project browser.png")
        if not USER.IS_DEVELOPER or True:
            self.tab_grid_level.Visibility = System.Windows.Visibility.Collapsed
            self.tab_subC_name.Visibility = System.Windows.Visibility.Collapsed


        self.Show()



    @ERROR_HANDLE.try_catch_error()
    def rename_view_Click(self, sender, e):
        sheets = forms.select_sheets(title = "Pick sheets that has the views to modify.")
        if not sheets:
            return
        is_default_format = self.radial_bt_is_sheetnum_detailnum_title.IsChecked
        is_original_flavor = self.radial_bt_is_original_flavor.IsChecked
        self.rename_view_event_handler.kwargs = doc, sheets, is_default_format, is_original_flavor
        self.ext_event_rename_view.Raise()
        res = self.rename_view_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"


    @ERROR_HANDLE.try_catch_error()
    def rename_family_click(self, sender, e):
        selection_ids = uidoc.Selection.GetElementIds ()
        if len(selection_ids) != 1:
            self.debug_textbox.Text = "Please select extactly one element."
            return
        selection = [doc.GetElement(x) for x in selection_ids]
        selected_element = selection[0]
        try:
            current_family_name = selected_element.Symbol.Family.Name
        except:
            self.debug_textbox.Text = "Cannot get the family name of the selection."
            return

        self.rename_family_event_handler.kwargs = selected_element,
        self.ext_event_rename_family.Raise()
        res = self.rename_family_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"

    @ERROR_HANDLE.try_catch_error()
    def view_prefix_modifier_click(self, sender, e):
        
        is_adding_prefix = self.radial_bt_prefix_add.IsChecked
        prefix = self.tbox_view_prefix.Text
        self.view_prefix_modifier_event_handler.kwargs = is_adding_prefix, prefix 
        self.ext_event_view_prefix_modifier.Raise()
        res = self.view_prefix_modifier_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"

            
    @ERROR_HANDLE.try_catch_error()
    def all_cap_view_name_click(self, sender, e):
        
        will_cap_sheet, will_cap_view =  True, True
        self.all_cap_view_event_handler.kwargs = will_cap_sheet, will_cap_view 
        self.ext_event_all_cap_view_name.Raise()
        res = self.all_cap_view_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"


    @ERROR_HANDLE.try_catch_error()
    def all_cap_spatical_element_name_click(self, sender, e):
        will_cap_room, will_cap_area =  True, True
        self.all_cap_spatical_element_event_handler.kwargs = will_cap_room, will_cap_area 
        self.ext_event_all_cap_spatial_element_name.Raise()
        res = self.all_cap_spatical_element_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"
    
    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()





@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    SuperRenamer()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":

    main()


