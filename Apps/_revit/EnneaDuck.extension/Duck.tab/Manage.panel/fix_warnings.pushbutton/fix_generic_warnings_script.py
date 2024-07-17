#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "In the standalone window, you can zoom in with section box to a region that have a warning.\n\nAs you are fixing it, you will see the warning count going down. When you sync baack after all the fix, the EA coins will be rewarded.."
__title__ = "Isolate\nWarnings"

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #

from EnneadTab import DATA_CONVERSION, ERROR_HANDLE
import traceback
from Autodesk.Revit import DB # pyright: ignore 
import random
# from Autodesk.Revit import UI # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
__persistentengine__ = True

@ERROR_HANDLE.try_catch_error
def make_3D_views_for_warning_cleaning():
    t = DB.Transaction(doc, "preaction view setting")
    t.Start()
    view = create_view("Generic")

    try:
        view.LookupParameter("Views_$Group").Set("Ennead")
        view.LookupParameter("Views_$Series").Set("Fix Errors  (°⌓°)")

        
    except:

        ERROR_HANDLE.print_note( traceback.format_exc())

    t.Commit()

    uidoc.ActiveView = view
    return view



def create_view(view_name):
    desired_name = "EnneadTab Warning Cleaning View_" + view_name
    view = get_view_by_name(desired_name)
    if view is not None:
        return view
    print ("####creating new axon view for " + view_name)
    view = DB.View3D.CreateIsometric (doc, get_threeD_view_type().Id)
    view.Name = desired_name
    return view

def get_view_by_name(name):
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    for view in all_views:
        if name == view.Name:
            return view
    return None

def get_threeD_view_type():
    view_family_types = DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()
    return filter(lambda x: x.ViewFamily == DB.ViewFamily.ThreeDimensional, view_family_types)[0]


def get_current_warning_count():
    return len(doc.GetWarnings())

@ERROR_HANDLE.try_catch_error
def random_pick(error_element_ids):

    try:
        min_pts = [doc.GetElement(el_id).get_BoundingBox(doc.ActiveView).Min for el_id in error_element_ids]
        max_pts = [doc.GetElement(el_id).get_BoundingBox(doc.ActiveView).Max for el_id in error_element_ids]


        min_X = min([pt.X for pt in min_pts])
        min_Y = min([pt.Y for pt in min_pts])
        min_Z = min([pt.Z for pt in min_pts])
        max_X = max([pt.X for pt in max_pts])
        max_Y = max([pt.Y for pt in max_pts])
        max_Z = max([pt.Z for pt in max_pts])


        bbox = DB.BoundingBoxXYZ()
        bbox.Min = DB.XYZ(min_X, min_Y, min_Z)
        bbox.Max = DB.XYZ(max_X, max_Y, max_Z)
    except Exception as e:
        #print (e)
        #print "This is usually becasue 2D element has no 3d boudning box"
        bbox = None




    uidoc.Selection.SetElementIds(DATA_CONVERSION.list_to_system_list(error_element_ids))


    if bbox:
        t = DB.Transaction(doc, "Random pick fixing apply sectionbox")
        t.Start()
        try:
            doc.ActiveView.SetSectionBox(bbox)
        except Exception as e:
            print (e)
        t.Commit()
        try:
            for uiview in uidoc.GetOpenUIViews():
                if uiview.ViewId == doc.ActiveView.Id:
                    uiview.ZoomToFit()
            uidoc.RefreshActiveView()
        except:
            print (traceback.format_exc())
        return
    #print error_element_ids
    uidoc.ShowElements(DATA_CONVERSION.list_to_system_list(error_element_ids))


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
class generic_warning_fixer_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """
    @ERROR_HANDLE.try_catch_error
    def pre_actions(self):

        #print "doing preaction"
        # get 3d view as current, set only show wall and sp line OST, not other curtain panles.

        # set EA helper

        self.simple_event_handler = SimpleEventHandler(random_pick)
        #self.clock_event_handler = SimpleEventHandler(clock_work)
        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.simple_event_handler)

        try:
            self.main_fix_view = make_3D_views_for_warning_cleaning()
        except:
            print (traceback.format_exc())
            self.main_fix_view = doc.ActiveView



        return

    def __init__(self):
        self.pre_actions()

        xaml_file_name = "fix_general_warning_ModelessForm.xaml"
        WPFWindow.__init__(self, xaml_file_name)
        self.initial_count = get_current_warning_count()
        self.title_text.Text = "Get to fix different kind of warnings one at a time."
        self.sub_text_counter.Text = "Initial warning count when the tool started = {}".format(self.initial_count)
        self.sub_text.Text = "Current total warnings = {}".format(self.initial_count)

        self.primary_button.Content = "Randomly bring me to a warning area."
        self.Title = "EnneadTab generic warning fixer."
        self.Width = 600
        self.Height = 400
        self.warning_category = None
        self.Show()


    @ERROR_HANDLE.try_catch_error
    def primary_button_click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        #print "primary button clicked"
        self.sub_text.Text = "Current total warnings = {}".format(get_current_warning_count())
        if not self.warning_category:
            self.category_text.Text = "No Warning Category Picked."
            return

        all_warnings = doc.GetWarnings()

        #  shorten to warning s about wall and rm sp line overlap
        warnings = filter(lambda x: self.warning_category in x.GetDescriptionText(), all_warnings)
        if len(warnings) == 0:
            self.category_text.Text = "There is no more warning in this category.\nGo pick another warning category."
            return


        uidoc.ActiveView = self.main_fix_view
        random.shuffle(warnings)
        warning = warnings[0]

        error_element_ids = list(warning.GetFailingElements())

        self.simple_event_handler.kwargs = error_element_ids,
        self.ext_event.Raise()
        # default_run_event.Raise()


    @ERROR_HANDLE.try_catch_error
    def close_button_click(self, sender, e):

        #print "close button clicked"
        self.Close()





    @ERROR_HANDLE.try_catch_error
    def pick_warning_category(self, sender, e):
        all_warnings = doc.GetWarnings()

        warning_dicts = dict()
        for warning in all_warnings:
            current_description = warning.GetDescriptionText()
            warning_dicts[current_description] = warning_dicts.get(current_description, 0) + 1



        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "[{}] {}".format(warning_dicts[self.item], self.item)

        opts = [MyOption(x) for x in warning_dicts.keys()]
        self.warning_category = forms.SelectFromList.show(opts, title = "Select the warnings you want to fix.", button_name='Select Warnings',multiselect  = False)
        if not self.warning_category:
            self.warning_category = opts[0].item

        self.category_text.Text = self.warning_category


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    modeless_form = generic_warning_fixer_ModelessForm()






