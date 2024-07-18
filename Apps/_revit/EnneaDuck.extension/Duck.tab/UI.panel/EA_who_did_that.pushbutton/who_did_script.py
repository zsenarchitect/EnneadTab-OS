#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "A floating window that give you information of the creator, editor and owner of selected elements and active view."
__title__ = "What\nHappened?"
__tip__ = True

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from System import EventHandler, Uri
import System


from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import _HostApplication
from pyrevit import HOST_APP

import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_SELECTION, REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE, IMAGE
import traceback
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True






@ERROR_HANDLE.try_catch_error()
def placeholder(ref_tag, bad_tags, is_V):

    t = DB.Transaction(doc, "tag align")
    t.Start()
    map(lambda x:process_tag(ref_tag, x, is_V), bad_tags)
    t.Commit()




# Create a subclass of IExternalEventHandler
class who_did_that_SimpleEventHandler(IExternalEventHandler):
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
class who_did_that_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.simple_event_handler = who_did_that_SimpleEventHandler(placeholder)

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

        xaml_file_name = "who_did_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "What Happened?"

        self.sub_text.Text = "Figure out what have happened to selected elements and current view by showing the creator, last editor and current owener of them. This window can stay open when your selection or active view change."


        self.Title = self.title_text.Text

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.selection = None


        self.hostapp = HOST_APP#_HostApplication(__revit__)
        if self.hostapp.is_newer_than(version = 2023, or_equal = True):
            self.main_who_did_bt.Visibility = System.Windows.Visibility.Collapsed
            from Autodesk.Revit.UI.Events import SelectionChangedEventArgs
            __revit__.SelectionChanged += EventHandler[SelectionChangedEventArgs](self.selection_update_event_handler_function)
        
        
        from Autodesk.Revit.UI.Events import ViewActivatedEventArgs 
        __revit__.ViewActivated += EventHandler[ViewActivatedEventArgs ](self.view_update_event_handler_function)
        
        self.update_active_view_info()
        self.Show()



    @ERROR_HANDLE.try_catch_error()
    def view_update_event_handler_function(self,sender, args):
        self.update_active_view_info()

    @ERROR_HANDLE.try_catch_error()
    def update_active_view_info(self):
        try:
            doc.ActiveView
        except:
            self.active_view_info_textbox.Text = "Cannot obtain active view information."
            
            return 
        if not doc.ActiveView:
            self.active_view_info_textbox.Text = "Cannot obtain active view information. Doc = {}".format(doc.Title)
            return
        note = "ActiveView: {}\n{}".format(doc.ActiveView.Name, REVIT_SELECTION.get_tooltip_info(doc, doc.ActiveView))
        self.active_view_info_textbox.Text = note


    @ERROR_HANDLE.try_catch_error()
    def selection_update_event_handler_function(self,sender, args):

        """
        have to wrap entire ting in try catch becasue G keep forgetting to close/unsubscribe who did that properly so there are always error emaill
        """
        try:
            selection_ids = list(args.GetSelectedElements ())
            
            if len(selection_ids) == 0:
                self.selection_info_textbox.Text = "No selection"
                return
    
            self.selection = []
            for x in selection_ids:

                self.selection.append(doc.GetElement(DB.ElementId(x.IntegerValue)))

            self.update_selection_info()
            
            
        except Exception as e:
            # print (e)
            return


    @ERROR_HANDLE.try_catch_error()
    def update_selection_info(self):
        if not self.selection or len(self.selection) == 0:
            self.selection_info_textbox.Text = "No selection"
            return
        note = ""
        for i, element in enumerate([x for x in self.selection if x is not None]):
            if i > 8:
                note += "...{} more elements selected...".format(len(self.selection) - i)
     
                break
            if hasattr(element, "Category") and hasattr(element.Category, "Name"):
                note += "{}\n".format(element.Category.Name)
            else:
                note += "{}\n".format(element)


            
            note += REVIT_SELECTION.get_tooltip_info(doc, element) + "\n\n"
        self.selection_info_textbox.Text = note.rstrip("\n\n")


    @ERROR_HANDLE.try_catch_error()
    def show_main_info_click(self, sender, args):
            
        selection_ids = uidoc.Selection.GetElementIds ()
        self.selection = [doc.GetElement(x) for x in selection_ids]
        self.update_selection_info()


    @ERROR_HANDLE.try_catch_error()
    def pick_template_click(self, sender, args):
        from pyrevit import forms
        templates = forms.select_viewtemplates()
        # print templates
        if not templates:
            return
        for template in templates:
            print ("################\nTemplate Name : {}\nTemplate Type : {}\n\n".format(template.Name, template.ViewType))
            print (REVIT_SELECTION.get_tooltip_info(doc, template))
            
            print ("\n\n")
        


    @ERROR_HANDLE.try_catch_error()
    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()
        if self.hostapp.is_newer_than(version = 2023, or_equal = True):
            try:
                from Autodesk.Revit.UI.Events import SelectionChangedEventArgs
                __revit__.SelectionChanged -= EventHandler[SelectionChangedEventArgs](self.selection_update_event_handler_function)
            except:
                pass
            
        # in case application has no ViewActivatred event...reason unknown
        try:
            from Autodesk.Revit.UI.Events import ViewActivatedEventArgs 
            __revit__.ViewActivated -= EventHandler[ViewActivatedEventArgs ](self.view_update_event_handler_function)
        except:
            pass
    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()






################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    try:
        modeless_form = who_did_that_ModelessForm()
        
    except:
        print (traceback.format_exc())
