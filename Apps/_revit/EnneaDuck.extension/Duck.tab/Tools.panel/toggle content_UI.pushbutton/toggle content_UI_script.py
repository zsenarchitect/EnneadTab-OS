#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """Control some pin and unpin status, or hide un hide status, or bubble head.

You can play with many different categories to control."""
__title__ = "Toggle\nContents"
__tip__ = True

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException



from pyrevit import script, forms



from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ENVIRONMENT, DATA_CONVERSION, ERROR_HANDLE


import traceback


uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True




@ERROR_HANDLE.try_catch_error()
def toggle_bubble(is_grid):
    selection_ids = uidoc.Selection.GetElementIds ()
    selection = [doc.GetElement(x) for x in selection_ids]
    selection = filter(lambda x: x.Category, selection )
    selection = filter(lambda x: x.Category.Name, selection )
    if is_grid:
        elements= filter(lambda x: x.Category.Name == "Grids", selection)
    else:
        elements= filter(lambda x: x.Category.Name == "Levels", selection)


    t = DB.Transaction(doc, "Toggle Bubble Head")
    t.Start()
    for el in elements:

        end0 = el.IsBubbleVisibleInView(DB.DatumEnds.End0,doc.ActiveView)
        end1 = el.IsBubbleVisibleInView(DB.DatumEnds.End1,doc.ActiveView)
        #print "xxx"
        #print end0,end1
        #print "xxxx"
        if end0 == end1:
            #print "#1"
            continue

        elif end0 and not(end1):
            #print "#2"
            el.ShowBubbleInView(DB.DatumEnds.End1,doc.ActiveView)
            el.HideBubbleInView(DB.DatumEnds.End0,doc.ActiveView)

        elif not(end0) and end1:
            #print "#3"
            el.ShowBubbleInView(DB.DatumEnds.End0,doc.ActiveView)
            el.HideBubbleInView(DB.DatumEnds.End1,doc.ActiveView)

        else:
            print("something wrong")


    doc.Regenerate()
    uidoc.Selection.SetElementIds(DATA_CONVERSION.list_to_system_list([x.Id for x in elements]))
    t.Commit()


@ERROR_HANDLE.try_catch_error()
def toggle_pin(category, to_pin, is_active_view_only):
    """to_pin:bool"""

    t = DB.Transaction(doc, "Toggle Pin")
    t.Start()
    if is_active_view_only:
        collector = DB.FilteredElementCollector(doc, doc.ActiveView.Id)
    else:
        collector = DB.FilteredElementCollector(doc)

    if isinstance(category, str):
        if category == "Curtain Wall":
            walls = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
            walls = [x for x in walls if hasattr(x, "WallType")]
            elements = filter(lambda x: str(x.WallType.Kind) == "Curtain", walls)
    else:
        elements = collector.OfCategory(category).WhereElementIsNotElementType().ToElements()

    count = 0
    for element in elements:
        if element.Pinned != to_pin:
            element.Pinned = to_pin
            count += 1
    t.Commit()
    uidoc.Selection.SetElementIds(DATA_CONVERSION.list_to_system_list([x.Id for x in elements]))
    return count



def hide_viewport_border(sheets, to_hide):
    to_show = not(to_hide)
    count = 0


    for sheet in sheets:
        view_ids = sheet.GetAllPlacedViews ()
        for view_id in view_ids:
            view = doc.GetElement(view_id)
            if view.CropBoxVisible != to_show:
                view.CropBoxVisible = to_show
                count += 1
    return count

def hide_OST(sheets, categories, to_hide, is_temp_view_property_only):
    count = 0
    for sheet in sheets:
        view_ids = sheet.GetAllPlacedViews ()
        for view_id in view_ids:
            view = doc.GetElement(view_id)
            if view.ViewType.ToString() in ["Schedule", "Legend", "Rendering", "ColumnSchedule"]:
                continue

            print("\n\n Processing <{}>".format(view.Name))
            view.EnableTemporaryViewPropertiesMode(view.Id)

            status = "hidden" if to_hide else "shown"
            for cate in categories:
                if not hasattr(cate, "Id"):
                    # static method to get category object from builtincategory
                    cate = DB.Category.GetCategory(doc, cate)

                if view.GetCategoryHidden (cate.Id) == to_hide:
                    print(cate.Name + " already " + status)
                    continue
                try:
                    view.SetCategoryHidden (cate.Id, to_hide)
                    print(cate.Name + " is now " + status)
                    count += 1
                except:
                    print("$$ Cannot modify " + cate.Name)

    return count


@ERROR_HANDLE.try_catch_error()
def toggle_hide(sheets, categories, to_hide, is_temp_view_property_only):
    """to_hide:bool"""

    t = DB.Transaction(doc, "Toggle Hide")
    t.Start()
    if isinstance(categories, str):
        if categories == "viewport_border":
            count = hide_viewport_border(sheets, to_hide)

    else:
        count = hide_OST(sheets, categories, to_hide, is_temp_view_property_only)

    t.Commit()
    return count

@ERROR_HANDLE.try_catch_error()
def reset_temp_template(sheets):


    t = DB.Transaction(doc, "Reset temp template")
    t.Start()
    count = 0
    for sheet in sheets:
        view_ids = sheet.GetAllPlacedViews ()
        for view_id in view_ids:
            view = doc.GetElement(view_id)
            if view.ViewType.ToString() in ["Schedule", "Legend", "Rendering", "ColumnSchedule"]:
                continue

            print("\n\n Processing <{}>".format(view.Name))
            if view.IsTemporaryViewPropertiesModeEnabled ():
                view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryViewProperties)
                count += 1

    t.Commit()
    return count


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
class ToggleContent_UI(forms.WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.toggle_bubble_event_handler = SimpleEventHandler(toggle_bubble)
        # We now need to create the ExternalEvent
        self.ext_event_toggle_bubble = ExternalEvent.Create(self.toggle_bubble_event_handler)



        self.toggle_pin_event_handler = SimpleEventHandler(toggle_pin)
        # We now need to create the ExternalEvent
        self.ext_event_toggle_pin = ExternalEvent.Create(self.toggle_pin_event_handler)


        self.toggle_hide_event_handler = SimpleEventHandler(toggle_hide)
        # We now need to create the ExternalEvent
        self.ext_event_toggle_hide = ExternalEvent.Create(self.toggle_hide_event_handler)


        self.reset_temp_template_event_handler = SimpleEventHandler(reset_temp_template)
        # We now need to create the ExternalEvent
        self.ext_event_reset_temp_template = ExternalEvent.Create(self.reset_temp_template_event_handler)
        return


    def __init__(self):

        self.pre_actions()
        xaml_file_name = 'toggle content_UI.xaml'
        forms.WPFWindow.__init__(self, xaml_file_name)
        self.subtitle.Text = "A floating window that helps with several common toggle actions."

        if ENVIRONMENT.IS_LOCAL_OS:
            logo_file = "{}\logo_vertical_light.png".format(ENVIRONMENT.OS_CORE_IMAGES_FOLDER)
        else:
            logo_file = "{}\logo_vertical_light.png".format(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT)
        import os
        if not os.path.exists(logo_file):
            logo_file = "{}\logo_vertical_light_temp.png".format(ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT) # note to self, remove this line so not to confuse later after IT fix peer link
        self.set_image_source(self.logo_img, logo_file)
        self.Height = 800

        self.selected_sheets = None
        self.selected_categories = None
        self.Show()




    @ERROR_HANDLE.try_catch_error()
    def bt_pin_dim_click(self, sender, args):
        self.pin_click(DB.BuiltInCategory.OST_Dimensions)

    @ERROR_HANDLE.try_catch_error()
    def bt_pin_keynote_tag_click(self, sender, args):
        self.pin_click(DB.BuiltInCategory.OST_KeynoteTags)

    @ERROR_HANDLE.try_catch_error()
    def bt_pin_viewport_click(self, sender, args):
        self.pin_click(DB.BuiltInCategory.OST_Viewports)

    @ERROR_HANDLE.try_catch_error()
    def bt_pin_titleblock_click(self, sender, args):
        self.pin_click(DB.BuiltInCategory.OST_TitleBlocks)

    @ERROR_HANDLE.try_catch_error()
    def bt_pin_cw_click(self, sender, args):
        self.pin_click("Curtain Wall")

    @ERROR_HANDLE.try_catch_error()
    def bt_pin_grid_click(self, sender, args):
        self.pin_click(DB.BuiltInCategory.OST_Grids)

    @ERROR_HANDLE.try_catch_error()
    def bt_pin_level_click(self, sender, args):
        self.pin_click(DB.BuiltInCategory.OST_Levels)

    @ERROR_HANDLE.try_catch_error()
    def pin_click(self, category):
        """pin unpin"""
        to_pin = self.radial_bt_is_pin.IsChecked
        is_active_view_only = self.radial_bt_is_current_view_only.IsChecked
        #is_active_view_only = True
        #print to_pin
        #print is_active_view_only
        #return
        self.toggle_pin_event_handler.kwargs = category, to_pin, is_active_view_only
        self.ext_event_toggle_pin.Raise()
        res = self.toggle_pin_event_handler.OUT

        verb = "pinned" if to_pin else "unpinned"
        self.debug_textbox.Text = "{} elements {}.".format(res, verb)

    def toggle_bubble_click(self, sender, args):
        """bubble"""
        self.toggle_bubble_event_handler.kwargs = self.radial_bt_is_grid.IsChecked,
        self.ext_event_toggle_bubble.Raise()
        res = self.toggle_bubble_event_handler.OUT





    @ERROR_HANDLE.try_catch_error()
    def bt_pick_sheets_click(self, sender, args):
        self.selected_sheets = forms.select_sheets()
        if not self.selected_sheets:
            return
        self.txtbk_pick_sheet.Text = "{} sheets picked".format(len(self.selected_sheets))


    @ERROR_HANDLE.try_catch_error()
    def bt_hide_pick_category_click(self, sender, args):
        all_categories = [x for x in doc.Settings.Categories if ".dwg" not in x.Name.lower()]
        all_categories.sort(key = lambda x: x.Name)
        self.selected_categories = forms.SelectFromList.show(all_categories,
                                                multiselect = True,
                                                name_attr = "Name",
                                                title = "Pick categories that you want to process.",
                                                button_name = 'Select Categories')

        if not self.selected_categories:
            self.label_selected_OST.Text = "Selected OST: "
            return

        note = ""
        for x in self.selected_categories:
            note += "\n{}".format(x.Name)
        self.label_selected_OST.Text = "Selected OST: " + note


    @ERROR_HANDLE.try_catch_error()
    def bt_hide_run_click(self, sender, args):
        if not self.selected_categories:
            return
        self.hide_click(self.selected_categories)


    @ERROR_HANDLE.try_catch_error()
    def bt_viewport_border_click(self, sender, args):
        self.hide_click("viewport_border")

    @ERROR_HANDLE.try_catch_error()
    def bt_hide_rm_sp_line_click(self, sender, args):
        self.hide_click(DB.BuiltInCategory.OST_RoomSeparationLines)

    @ERROR_HANDLE.try_catch_error()
    def bt_hide_area_sp_line_click(self, sender, args):
        self.hide_click(DB.BuiltInCategory.OST_AreaSchemeLines)

    @ERROR_HANDLE.try_catch_error()
    def bt_hide_sectionbox_click(self, sender, args):
        self.hide_click(DB.BuiltInCategory.OST_SectionBox)

    @ERROR_HANDLE.try_catch_error()
    def bt_hide_scopebox_click(self, sender, args):
        self.hide_click(DB.BuiltInCategory.OST_VolumeOfInterest)

    @ERROR_HANDLE.try_catch_error()
    def bt_hide_level_click(self, sender, args):
        self.hide_click(DB.BuiltInCategory.OST_Levels)



    @ERROR_HANDLE.try_catch_error()
    def hide_click(self, category):
        """hide unhide"""
        sheets = self.selected_sheets
        if not sheets:
            return
        to_hide = self.radial_bt_is_hide.IsChecked
        is_temp_view_property_only = self.checkbox_bt_is_temp_view_only.IsChecked
        if isinstance(category, str):
            categories = category
        elif not isinstance(category, list):
            categories = [category]
        elif isinstance(category, list):
            categories = category
        else:
            print("!!!Something wrong, tell SZ")

        self.toggle_hide_event_handler.kwargs = sheets, categories, to_hide, is_temp_view_property_only
        self.ext_event_toggle_hide.Raise()
        res = self.toggle_hide_event_handler.OUT

        verb = "hided" if to_hide else "unhided"
        self.debug_textbox.Text = "{} elements {}.".format(res, verb)

    @ERROR_HANDLE.try_catch_error()
    def bt_reset_temp_template_click(self, sender, args):
        sheets = self.selected_sheets
        if not sheets:
            return

        self.reset_temp_template_event_handler.kwargs = sheets,
        self.ext_event_reset_temp_template.Raise()
        res = self.reset_temp_template_event_handler.OUT


        self.debug_textbox.Text = "{} elements reset.".format(res)


    def handleclick(self, sender, args):
        print ("surface clicked")

    def close_click(self, sender, args):
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()



@ERROR_HANDLE.try_catch_error()
def main():

    modeless_form = ToggleContent_UI()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
    
