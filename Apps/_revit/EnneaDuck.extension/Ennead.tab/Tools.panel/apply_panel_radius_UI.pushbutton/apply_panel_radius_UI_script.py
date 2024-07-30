#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Pick curtain panel type and apply host wall radius to panel radius on parameter defined by user."
__title__ = "Apply Panel\nRadius"
__tip__ = True

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException




from pyrevit import script, forms


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import IMAGE, NOTIFICATION, DATA_CONVERSION, ERROR_HANDLE


import traceback
import random

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True



def get_all_instance_of_type(type):

    type_filter = DB.FamilyInstanceFilter (doc, type.Id)
    instances = list(DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance).WherePasses (type_filter).ToElements())

    return instances


@ERROR_HANDLE.try_catch_error()
def apply_radius_action(window):
    t = DB.Transaction(doc, __title__)
    t.Start()
    solution = Solution(window.bad_type, window.para_textbox.Text)

    # get all instacen of bad family, first check can we get a matching type name, record all instacne data
    bad_instances = get_all_instance_of_type(solution.bad_type)

    if len(bad_instances) == 0:
        note = "Cannot get anything from {}".format(solution.bad_type.LookupParameter("Type Name").AsString())
        REVIT_FORMS.notification(main_text = note,
                                                sub_text = "There might be no instance of bad type in the file, you should try purging.",
                                                window_title = "EnneadTab",
                                                button_name = "Close",
                                                self_destruct = 15,
                                                window_width = 1200)

        return

    output.print_md( "--Applying Panel Radius By Host Wall **[{}]:{}** ----Found {} Items".format(solution.bad_type.Family.Name,
                                            solution.bad_type.LookupParameter("Type Name").AsString(),
                                            len(bad_instances)))
    #print all_instances
    map(solution.fix_panel, bad_instances)
    #envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED")
    #envvars.set_pyrevit_env_var("EA_INSTANCE_DATA_TRANSFER", DATA)








    NOTIFICATION.messenger(sub_text = "",
                                main_text = "Radius Applied Finished!")


    t.Commit()
    window.update_drop_down_selection_source()
    text_out = "Radius Applied:\n[{}]: {} --> {} fixed.".format(solution.bad_type.Family.Name,
                                                            solution.bad_type.LookupParameter("Type Name").AsString(),
                                                            solution.fix_count)
    window.debug_textbox.Text = text_out
    window.debug_textbox.FontSize = 12

class Solution:
    def __init__(self, bad_type, para_name):
        self.bad_type = bad_type
        self.para_name = para_name


        self.error_panel_found = False
        self.fix_count = 0


    def fix_panel(self, panel):
        if not panel.LookupParameter(self.para_name):
            return

        desires_r = self.find_panel_host_wall_radius(panel)
        if panel.LookupParameter(self.para_name).AsDouble() != desires_r:
            panel.LookupParameter(self.para_name).Set(desires_r)
            self.fix_count += 1

    def find_panel_host_wall_radius(self, panel):

        radius = panel.Host.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_ARC_RADIUS).AsDouble()
        if radius == 0.0:
            print("Panel {} should be in curved wall.{}".format(panel.Id, output.linkify(panel.Id,title = "Click to zoom to panel")))

            self.error_panel_found = True

        return radius


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

class DropDownItem():
    def __init__(self, item):
        if isinstance(item, str):
            self.item = item
            self.display_text = item
            return

        self.item = item
        self.display_text = item.LookupParameter("Type Name").AsString()


# A simple WPF form used to call the ExternalEvent
class apply_panel_radius_UI(forms.WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.apply_radius_action_event_handler = SimpleEventHandler(apply_radius_action)
        #self.clock_event_handler = SimpleEventHandler(clock_work)
        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.apply_radius_action_event_handler)
        #self.ext_event_clock = ExternalEvent.Create(self.clock_event_handler)
        #print "preaction done"
        #print self.apply_radius_action_event_handler
        #print self.apply_radius_action_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return


    def __init__(self):

        self.pre_actions()
        xaml_file_name = 'apply_panel_radius_UI.xaml'
        forms.WPFWindow.__init__(self, xaml_file_name)

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.Height = 800
        self.family_bad = None
        self.Show()


    @property
    def bad_type(self):
        if not self.type_list_bad.SelectedItem:
            return None
        return doc.GetElement(self.type_list_bad.SelectedItem.item.Id)







    @ERROR_HANDLE.try_catch_error()
    def apply_radius_clicked(self, sender, args):



        self.apply_radius_action_event_handler.kwargs = self,
        self.ext_event.Raise()







    def open_details_describtion(self, sender, args):
        main_text = "How to use Panel Radius Apply?"
        sub_text = "\n\nStep 1: Pick curtain panel family"
        sub_text += "\nStep 2: Pick the type"
        sub_text += "\nStep 3(Optional): Preview the panel by clicking the zoom."
        sub_text += "\nStep 4: Input the instance parameter where you want to load the wall radius info."
        sub_text += "\nStep 5: Apply radius"
        REVIT_FORMS.notification(main_text = main_text,
                                                sub_text = sub_text,
                                                window_title = "EnneadTab",
                                                button_name = "Close",
                                                self_destruct = 15,
                                                window_width = 1200,
                                                window_height = 800)


    def open_youtube(self, sender, args):
        REVIT_FORMS.notification(main_text = "not recorded yet",
                                                sub_text = "blah blah blah",
                                                window_title = "EnneadTab",
                                                button_name = "Close",
                                                self_destruct = 15,
                                                window_width = 1200,
                                                window_height = 800)
        return
        script.open_url(r"https://youtu.be/gb2rG6ZteP8")


    @ERROR_HANDLE.try_catch_error()
    def pick_type_bad(self, sender, args):
        #print "pick bad type"
        self.family_bad = self.get_family()




    def get_family(self):

        families = DB.FilteredElementCollector(doc).OfClass(DB.Family).WhereElementIsNotElementType().ToElements()
        families = sorted(families, key = lambda x: x.Name.lower())
        for family in families:
            if family.FamilyCategory.Name == "Curtain Panels":
                family_id = family.FamilyCategoryId
                break

        families = filter(lambda x: x.FamilyCategoryId == family_id, families)


        family = forms.SelectFromList.show(families,
                                            multiselect = False,
                                            name_attr = 'Name',
                                            width = 600,
                                            title = "Pick family",
                                            button_name = 'Select Curtain Panel Family')
        if not family:
            return
        self.family_bad = family
        self.family_name_bad.Text = family.Name
        self.type_list_bad.SelectedIndex = 0

        self.update_drop_down_selection_source()
        return family



    def get_types(self, family):
        if not family or not family.IsValidObject :
            return []
        if len(family.GetFamilySymbolIds ()) == 0:
            return []
        types = [doc.GetElement(x) for x in family.GetFamilySymbolIds ()]
        types = sorted(types, key = lambda x: x.LookupParameter("Type Name").AsString())
        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "{}".format(self.LookupParameter("Type Name").AsString())
        types = [MyOption(x) for x in types]
        return types

    def update_drop_down_selection_source(self):

        #raw_subC_names = ["- Waiting Assignment -"] +  get_all_subC_names() + ["<Use Source File Name as SubC>"]
        # self.type_list_bad.ItemsSource = self.get_types(self.family_bad)
        # self.type_list_target.ItemsSource = self.get_types(self.family_target)
        selected_index = max(self.type_list_bad.SelectedIndex, 0)
        #print "%%%%%%%%%%"
        #print selected_index
        self.type_list_bad.ItemsSource = [DropDownItem(x) for x in self.get_types(self.family_bad)]
        self.type_list_bad.SelectedIndex = min(selected_index, len(self.type_list_bad.ItemsSource) - 1)
        #print self.type_list_bad.SelectedIndex
        #print "^^^^^^^"



    def dropdown_list_value_changed(self, sender, args):
        return
        #self.is_pass_convert_precheck()
        print(self.type_list_bad.ItemsSource)
        for x in self.type_list_bad.ItemsSource:
            print(x)
            print(x.item)
            print(x.display_text)




    def zoom_bad_click(self, sender, args):
        self.handle_zoom()

    @ERROR_HANDLE.try_catch_error()
    def handle_zoom(self):

        if not self.bad_type:
            return

        instances = get_all_instance_of_type(self.bad_type)
        if len(instances) == 0:
            NOTIFICATION.messenger(main_text = "Found no elements of this type.", force_toast = True)
            return
        random.shuffle(instances)
        instance = instances[0]
        uidoc.ShowElements(instance)
        uidoc.Selection.SetElementIds(DATA_CONVERSION.list_to_system_list([instance.Id]))


    def handleclick(self, sender, args):
        print ("surface clicked")

    def close_click(self, sender, args):
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()



@ERROR_HANDLE.try_catch_error()
def main():

    modeless_form = apply_panel_radius_UI()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
    
