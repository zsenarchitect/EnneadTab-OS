#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "A floating window that give you quick access to add dim text below your selected dim or dims.\nYou can use any of the popular dim text, or use your own by typing in the user bar.\nYou may also pick the relative position on the text to the default numbering.(Up, Down, Prefix, Surfix)"
__title__ = "Dim Text\nHelper"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=29672"
__youtube__ = "https://youtu.be/WYs-_k5IV48"
__tip__ = True
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #

import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import IMAGE, ERROR_HANDLE
import traceback
from Autodesk.Revit import DB # pyright: ignore 

from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True




@ERROR_HANDLE.try_catch_error()
def mark_dim_text(target_text, position):



    selection_ids = uidoc.Selection.GetElementIds ()
    if len( selection_ids) == 0:
        return "Nothing selected."
    selection = [doc.GetElement(x) for x in selection_ids]

    selection = filter(lambda x: x.Category.Name == "Dimensions", selection )
    """
    for x in selection:
        if x.Category.Name != "Dimensions":
            return "Find non-dimension element in selection. {}".format(x.Category.Name
    """


    t = DB.Transaction(doc, "dim segement")
    t.Start()
    count = 0
    for dim in selection:

        if dim.NumberOfSegments == 0:
            #print "ok, 0 segement"
            setattr(dim, position, target_text)
            count += 1
            continue

        #print "ah, dim with many segements"
        for dim_seg in dim.Segments:
            setattr(dim_seg, position, target_text)
            count += 1
    t.Commit()
    return "{} dim text added.".format(count)

# Create a subclass of IExternalEventHandler
class dim_text_SimpleEventHandler(IExternalEventHandler):
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
class dim_text_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.simple_event_handler = dim_text_SimpleEventHandler(mark_dim_text)

        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.simple_event_handler)
        #print "preaction done"
        #print self.simple_event_handler
        #print self.simple_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return

    def __init__(self):
        self.pre_actions()

        xaml_file_name = "DimText_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Dim Text Helper"

        self.sub_text.Text = "Pick dim(s) from view and click below to add dim text.\n\nNon dimension objects will be auto-filtered off so you can cross select multiple categories.\n(AKA no need for precise slection.)"


        self.Title = "EnneadTab DimText Helper"

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.radial_button_below.IsChecked = True

        self.Show()


    def mark_empty_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click("")


    def mark_FOG_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click("FOG")


    def mark_EOS_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click("EOS")

    def mark_FTF_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click("FTF")

    def mark_FOW_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click("FOW")

    def mark_Spandrel_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click("Spandrel")

    def mark_X_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click("X")

    def mark_varies_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click("Varies")

    def mark_user_1_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click(self.user_define_textbox_1.Text)

    def mark_user_2_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click(self.user_define_textbox_2.Text)

    def clear_mark_user_1_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.user_define_textbox_1.Text = ""

    def clear_mark_user_2_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.user_define_textbox_2.Text = ""

    @property
    def text_position(self):
        if self.radial_button_above.IsChecked:
            return "Above"
        if self.radial_button_below.IsChecked:
            return "Below"
        if self.radial_button_prefix.IsChecked:
            return "Prefix"
        if self.radial_button_suffix.IsChecked:
            return "Suffix"

    @ERROR_HANDLE.try_catch_error()
    def generic_click(self, keyword):
        #print "Clicking " + keyword
        self.simple_event_handler.kwargs = keyword, self.text_position
        self.ext_event.Raise()
        res = self.simple_event_handler.OUT
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

    def position_changed(self, sender, args):
        pass

"""see thing below for learning on passing **kwargs and funcs to handler"""
class CustomizableEvent:
    def __init__(self):
        """ An instance of this class need to be created before any modeless operation.
        You can then call the raise_event method to perform any modeless operation.
        Any modification to Revit DB need to be performed inside a valid Transaction.
        This Transaction needs to be open inside the function_or_method, NOT before calling raise_event.
        >>> customizable_event = CustomizableEvent()
        >>> customizable_event.raise_event(rename_views, views_and_names)
        """
        # Create an handler instance and his associated ExternalEvent
        custom_handler = _CustomHandler()
        custom_handler.customizable_event = self
        self.custom_event = UI.ExternalEvent.Create(custom_handler)

        # Initialise raise_event variables
        self.function_or_method = None
        self.args = ()
        self.kwargs = {}

    def _raised_method(self):
        """ !!! DO NOT USE THIS METHOD IN YOUR SCRIPT !!!
        Method executed by IExternalEventHandler.Execute when ExternalEvent is raised by ExternalEvent.Raise.
        """
        self.function_or_method(*self.args, **self.kwargs)

    def raise_event(self, function_or_method, *args, **kwargs):
        """
        Method used to raise an external event with custom function and parameters
        Example :
        >>> customizable_event = CustomizableEvent()
        >>> customizable_event.raise_event(rename_views, views_and_names)
        """
        self.args = args
        self.kwargs = kwargs
        self.function_or_method = function_or_method
        self.custom_event.Raise()


class _CustomHandler(UI.IExternalEventHandler):
    """ Subclass of IExternalEventHandler intended to be used in CustomizableEvent class
    Input : function or method. Execute input in a IExternalEventHandler"""
    def __init__(self):
        self.customizable_event = None

    # Execute method run in Revit API environment.
    # noinspection PyPep8Naming, PyUnusedLocal
    def Execute(self, application):
        try:
            self.customizable_event._raised_method()
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print("InvalidOperationException catched")

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def GetName(self):
        return "Execute an function or method in a IExternalHandler"



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    try:
        modeless_form = dim_text_ModelessForm()
        
    except:
        print (traceback.format_exc())



