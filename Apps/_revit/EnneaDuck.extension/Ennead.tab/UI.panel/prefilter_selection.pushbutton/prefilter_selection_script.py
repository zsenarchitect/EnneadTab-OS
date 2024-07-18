#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """Just like the prefilter selection in Rhino, this allow you to narrow down selection beofre heavy window selection and post filter.
Very helpful when the drawing is very crowded.

You can enable multiple category at same time.

Let Sen.Z know if you would like to add more to the category list."""

# to-do: add feature to allow include/exclude elements in group. Make a big toggle ----> if element.GroupId == element.GroupId.InvalidElementId:


__title__ = "Prefilter\nSelection"
__tip__ = True


# from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 

from EnneadTab.REVIT import REVIT_FORMS, REVIT_SELECTION, REVIT_APPLICATION
from EnneadTab import NOTIFICATION, ERROR_HANDLE
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()





class PrefilterUI(REVIT_FORMS.EnneadTabModelessForm):
    
    
    def get_filter_toggle_bt(self):
        for item in dir(self):
            if item.startswith("toggle_bt_"):
                yield getattr(self, item)
                
    def update_cate_selection(self):
        self.selection_cate_setting = {}
        for item in self.get_filter_toggle_bt():
            self.selection_cate_setting[item.Name.replace("toggle_bt_", "")] = item.IsChecked

        # print (self.selection_cate_setting)

    @ERROR_HANDLE.try_catch_error()
    def select_click(self, sender, e):
                
        from EnneadTab.REVIT import REVIT_FORMS, REVIT_SELECTION, REVIT_APPLICATION
        from EnneadTab import NOTIFICATION, ERROR_HANDLE # need to import again after inherating class....this is a bug in pyrevit that has troubled me since SearchUI
        import os
        import sys
        if not self._toggle_bt_enabled.IsChecked:
            NOTIFICATION.messenger(main_text="Filter is disabled now...")
            return
        self.update_cate_selection()

        
        if True not in self.selection_cate_setting.values():
            NOTIFICATION.messenger(main_text="You have disabled all categories.")
            return
        
        NOTIFICATION.messenger(main_text="Go ahead and select in window now...")
        uidoc = REVIT_APPLICATION.get_uidoc()

        current_folder = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(current_folder)
        from cate_filter import CateFilter
        raw_elements = uidoc.Selection.PickElementsByRectangle(CateFilter(self.selection_cate_setting),
                                                                "Make a window selection now in your main window...")
        final_elements = [] # need to do this step to cast from List[] to pytho list
        for x in raw_elements:
            final_elements.append(x)
        
        REVIT_SELECTION.set_selection(final_elements)
        NOTIFICATION.messenger(main_text="{} elements selected.".format(len(final_elements)))
        uidoc.RefreshActiveView()
        return
        self.rename_view_event_handler.kwargs = sheets, is_default_format
        self.ext_event_rename_view.Raise()
        res = self.rename_view_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"

            

    @ERROR_HANDLE.try_catch_error()
    def reset_filter_click(self, sender, e):
        for item in self.get_filter_toggle_bt():
            item.IsChecked = False

    @ERROR_HANDLE.try_catch_error()     
    def toggle_enabler_click(self, sender, e):
        self.tblock_enabler.Text = "Filter is now Enabled " if self._toggle_bt_enabled.IsChecked else "Filter is now Disabled "
        for item in self.get_filter_toggle_bt():
            item.IsEnabled = self._toggle_bt_enabled.IsChecked

            
@ERROR_HANDLE.try_catch_error()
def prefilter_selection():

    external_funcs = []
    PrefilterUI(title=__title__.replace("\n", " "), 
                summery = __doc__,
                xaml_file_name="prefilter_selection_UI.xaml")
    

################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    prefilter_selection()
    


