#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "A floating window that help you correct worksets by category, by host or by type.\n\nContents inside design option can also change workset as long as they are not in group."
__title__ = "WorkSet\nManager"
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


from EnneadTab.REVIT import REVIT_FORMS, REVIT_SELECTION, REVIT_APPLICATION
from EnneadTab import ENVIRONMENT_CONSTANTS, SOUNDS, USER, ERROR_HANDLE
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True



import ENNEAD_LOG

def get_element_workset(element):
    return doc.GetWorksetTable().GetWorkset(element.WorksetId)

def change_workset(element, target_workset) :
    """
    return in_wrong_workset,is_fail_convert, log
    """
    if target_workset == "By Host":
        target_workset = get_element_workset(element.Host)


    #curent_workset_id = element.Parameters[DB.BuiltInParameter.ELEM_PARTITION_PARAM].AsElementId().IntegerValue

    curent_workset_id = get_element_workset(element).Id.IntegerValue
    if curent_workset_id == target_workset.Id.IntegerValue  :
        return False,False,None
    

    #print "{}, {},{}".format(output.linkify(element.Id, title = "Go To Element"), element.GroupId, element.DesignOption)
    ownership = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc,element.Id).Owner
    if ownership and (ownership != USER.get_autodesk_user_name()):
        log = "[Owndership] Cannot edit {0} due to ownership by {2}---> {1}".format(element.Id,output.linkify(element.Id, title = "Go To Element"),ownership)
        return True, True, log

    if element.ViewSpecific:
        log = "[View Specific] View Specific item has no user workset.-->{}".format(output.linkify(element.Id, title = "Go To Element"))
        return True, True, log

    """
    if element.GroupId.IntegerValue != -1 and element.DesignOption:
        # group in design option
        log = "[Group in Design Option] The element is in group '{}' and design option '{}'. -->{}\nYou may use 'Go To Element' while that group and design option is in edit mode.\n\n ".format(output.linkify(element.GroupId, title = "Go To Group"),element.DesignOption.Name, output.linkify(element.Id, title = "Go To Element"))
        return True, True, log
    """

    if element.GroupId.IntegerValue != -1: #-1 means not in group
        if element.DesignOption:
            log = "[Group in Design Option] The element is in group '{}' and design option '{}'. -->{}\nYou may use 'Go To Element' while that group and design option is in edit mode.\n\n ".format(output.linkify(element.GroupId, title = "Go To Group"),element.DesignOption.Name, output.linkify(element.Id, title = "Go To Element"))
            return True, True, log

        group_name = doc.GetElement(element.GroupId).Name
        log = "[Group] Fail to set workset becasue it is in group '{2}'---> {0}--->{1}".format(output.linkify(element.Id, title = "Go To Element"),output.linkify(element.GroupId, title = "Go To Group"), group_name)
        log += "This group is currently in workset '{}'".format(get_element_workset(doc.GetElement(element.GroupId)).Name)
        return True, True, log

    """
    if element.DesignOption:
        log = "[Design Option] The element is in design option '{}'.-->{}\nYou may use 'Go To Element' while that design option is in edit mode.\n\n ".format(element.DesignOption.Name, output.linkify(element.Id, title = "Go To Element"))
        return True, True, log
    """

    try:
        para = element.Parameter[DB.BuiltInParameter.ELEM_PARTITION_PARAM]
        if para.IsReadOnly :
            if hasattr(element, "SuperComponent"):
                if element.SuperComponent:
                    return True, True, "[Shared Nesting Family] The workset is determined by the parent family instance."
                
            # print (output.linkify(element.Id))
            return True, True, "[Read Only] The workset is read only."
        para.Set(target_workset.Id.IntegerValue)
    except Exception as e:
        print("Skipping workset change for element [{}] becasue {}".format(output.linkify(element.Id, title = "Go To Element"), e))
    log = None
    return True, False, log


def is_match_wall(my_wall, claimer):
    """this func is to deal with FaceWall class. Becasue wall by face object has no WallType attr"""
    if hasattr(my_wall, "WallType"):

        if my_wall.WallType.Id.IntegerValue == claimer.Id.IntegerValue:
            return True
        else:
            return False
    

    # for para in my_wall.Parameters:
    #     print para.Definition.Name
    if my_wall.LookupParameter("Type").AsElementId().IntegerValue == claimer.Id.IntegerValue:
        return True
    else:
        return False


def get_all_of_this(claimer):

    if isinstance(claimer, str):
        if "OST" in claimer:
            parser = getattr(DB.BuiltInCategory , claimer)
            all_elements = DB.FilteredElementCollector(doc).OfCategory(parser).WhereElementIsNotElementType().ToElements()
        else:
            parser = getattr(DB , claimer)
            all_elements = DB.FilteredElementCollector(doc).OfClass(parser).WhereElementIsNotElementType().ToElements()
            
            # make special case for ref plane
            if claimer == "ReferencePlane":
                all_elements = [x for x in all_elements if not x.LookupParameter("Workset").IsReadOnly]
    else:
        if hasattr(claimer, "IsFoundationSlab"):
            all_elements = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
            all_elements = [x for x in all_elements if x.FloorType.Id.IntegerValue == claimer.Id.IntegerValue]
        else:
            all_elements = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
            all_elements = [x for x in all_elements if is_match_wall(x, claimer)]


    return list(all_elements)


@ERROR_HANDLE.try_catch_error
def update_worksets(changed_cates):

    t = DB.Transaction(doc, "Update Worksets")
    t.Start()

    for obj in changed_cates:
        #print obj.format_name
        #print obj.selected_workset
        #print obj.claimer
        
        



        all_elements = get_all_of_this(obj.claimer)
        #print all_elements
        if len(all_elements) == 0:
            continue

        if obj.selected_workset == "By Host":
            target_workset = "By Host"
        else:
            target_workset = REVIT_SELECTION.get_workset_by_name(doc, obj.selected_workset)
        res = [change_workset(element, target_workset) for element in all_elements]
        in_wrong_workset_count = len([x for x in res if x[0] == True])
        is_fail_convert_count = len([x for x in res if x[1] == True])
        is_success_convert_count = in_wrong_workset_count - is_fail_convert_count
        log = [x[2] for x in res if x[2] != None]
        print("\n".join(log))
        
        fail_group_count = len([x for x in log if "[Group]" in x.lower()])
        fail_design_option_count = len([x for x in log if "[Design Option]" in x.lower()])
        fail_ownership_count = len([x for x in log if "[Owndership]" in x.lower()])
        fail_view_specific_count = len([x for x in log if "[View Specific]" in x.lower()])
        fail_group_and_design_option_count = len([x for x in log if "[Group in Design Option]" in x.lower()])

        note = ""
        if is_success_convert_count > 0:
            note += "{} elements successfully converted.\n".format(is_success_convert_count)
        if fail_ownership_count > 0:
            note += "{} failed due to ownership.\n".format(fail_ownership_count)
        if fail_group_count > 0:
            note += "{} failed due to in group.\n".format(fail_group_count)
        if fail_group_and_design_option_count > 0:
            note += "{} failed due to in group and design option.\n".format(fail_group_and_design_option_count)
        if fail_design_option_count > 0:
            note += "{} failed due to in design option.\n".format(fail_design_option_count)
        if fail_view_specific_count > 0:
            note += "{} failed due to view specific.\n".format(fail_view_specific_count)

        

        SOUNDS.play_sound("sound effect_happy bell.wav")
        REVIT_FORMS.notification(main_text = "For {}, {} elements found.\n{} of them in wrong workset.".format(obj.format_name, len(all_elements),in_wrong_workset_count, is_fail_convert_count ),
                                                  sub_text = note) #self_destruct = 10

    
    #print "\n\nDone!"

    t.Commit()




# Create a subclass of IExternalEventHandler
class workset_manage_SimpleEventHandler(IExternalEventHandler):
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


class data_grid_obj:
    def __init__(self, init_data):

        if isinstance(init_data, tuple):
            self.claimer = init_data[0]
            self.format_name = init_data[1]

        else:
            # feeding in type
            self.claimer = init_data
            self.format_name = init_data.LookupParameter("Type Name").AsString()


        self.selected_workset = "...Unchange..."
       


# A simple WPF form used to call the ExternalEvent
class workset_manage_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.simple_event_handler = workset_manage_SimpleEventHandler(update_worksets)

        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.simple_event_handler)
        #print "preaction done"
        #print self.simple_event_handler
        #print self.simple_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return


    @ERROR_HANDLE.try_catch_error
    def __init__(self):
        self.pre_actions()

        xaml_file_name = "fix_workset_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab WorkSet Manager"

        self.sub_text.Text = "Manage your worksets in this form. It can even change elements inside design options, as long as they are not in a group."


        self.Title = self.title_text.Text

        if ENVIRONMENT_CONSTANTS.IS_LOCAL_OS:
            logo_file = "{}\logo_vertical_light.png".format(ENVIRONMENT_CONSTANTS.OS_CORE_IMAGES_FOLDER)
        else:
            logo_file = "{}\logo_vertical_light.png".format(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT)
        import os
        if not os.path.exists(logo_file):
            logo_file = "{}\logo_vertical_light_temp.png".format(ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT) # note to self, remove this line so not to confuse later after IT fix peer link
        self.set_image_source(self.logo_img, logo_file)


        
        self.update_UI()

        

        self.Show()


    def init_drop_menu(self):
        if self.radio_bt_by_host.IsChecked:
             self.workset_combos.ItemsSource = ["...Unchange..."] + ['By Host']
        else:
            self.workset_combos.ItemsSource = ["...Unchange..."] + [x.Name for x in REVIT_SELECTION.get_all_userworkset(doc)]


    @ERROR_HANDLE.try_catch_error
    def init_data_grid(self):
        if self.radio_bt_by_cate.IsChecked:

            cate_list = [("OST_Grids", "Grids"),
                        ("OST_Levels", "Levels"),
                        ("OST_Rooms", "Rooms"),
                        ("OST_Areas", "Areas"),
                        ("OST_FurnitureSystems", "Furniture Systems"),
                        ("OST_Furniture", "Furniture"),
                        ("OST_Columns", "Architectural Columns"),
                        ("OST_StructuralColumns", "Structural Columns"),
                        ("OST_RoomSeparationLines", "Room Separation Lines"),
                        ("OST_AreaSchemeLines", "Area Boundary Lines"),
                        ("OST_RvtLinks", "Revit Link"),
                        ("ImportInstance", "DWG"),
                        ("OST_Mass", "Mass"),
                        ("ReferencePlane", "Ref Plane"),
                        ("OST_VolumeOfInterest", "ScopeBox")]
            self.main_data_grid.ItemsSource = [data_grid_obj(cate) for cate in cate_list]

        if self.radio_bt_by_host.IsChecked:
            cate_list = [("OST_Doors", "Doors"),
                        ("OST_Windows", "Windows")]

            self.main_data_grid.ItemsSource = [data_grid_obj(cate) for cate in cate_list]

        if self.radio_bt_by_type.IsChecked:
            if self.radio_bt_by_type_wall.IsChecked:
                type_list = list(DB.FilteredElementCollector(doc).OfClass(DB.WallType).ToElements())
            else:
                type_list = list(DB.FilteredElementCollector(doc).OfClass(DB.FloorType).ToElements())


            type_list.sort(key = lambda x: x.LookupParameter("Type Name").AsString())
            self.main_data_grid.ItemsSource = [data_grid_obj(type) for type in type_list]
        

    @ERROR_HANDLE.try_catch_error
    def preview_selection_changed(self, sender, args):
        obj = self.main_data_grid.SelectedItem
        if not obj:
            self.textblock_workset_detail.Text = ""
            return

        
        self.textblock_workset_detail.Text = "{} of {} in this project.".format(len(get_all_of_this(obj.claimer)), obj.format_name)


    @ERROR_HANDLE.try_catch_error
    def setting_changed(self, sender, args):
        self.update_UI()


    def update_UI(self):
        self.init_drop_menu()

        if self.radio_bt_by_type.IsChecked:
            self.by_type_detail_panel.IsEnabled = True
        else:
            self.by_type_detail_panel.IsEnabled = False

        self.init_data_grid()


    @ERROR_HANDLE.try_catch_error
    def update_worksets_click(self, sender, args):
        cates = self.main_data_grid.ItemsSource
        changed_cates = [obj for obj in cates if obj.selected_workset != "...Unchange..."]



        self.simple_event_handler.kwargs = changed_cates,
        self.ext_event.Raise()
        res = self.simple_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"




    @ERROR_HANDLE.try_catch_error
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

        modeless_form = workset_manage_ModelessForm()
        ENNEAD_LOG.use_enneadtab(coin_change = 100, tool_used = __title__.replace("\n", " "), show_toast = True)
    except:
        print (traceback.format_exc())
