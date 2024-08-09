#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "In the standalone window, you can zoom in with section box to a region that have wall and room seperation line overlay warning.\n\nAs you are fixing it, you will see the wanring count going down."
__title__ = "75_Fix Wall And Room sp_line Overlap"

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import traceback
from Autodesk.Revit import DB # pyright: ignore 
import random
# from Autodesk.Revit import UI # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
__persistentengine__ = True


def make_3D_views_for_warning_cleaning():
    t = DB.Transaction(doc, "preaction view setting")
    t.Start()
    view = create_view("Wall SP line overlap")

    """
    for view, workset in zip(views, worksets):
        view.SetWorksetVisibility(workset.Id, DB.WorksetVisibility.Visible)
        for other_workset in worksets:
            if other_workset == workset:
                continue
            view.SetWorksetVisibility(other_workset.Id, DB.WorksetVisibility.Hidden)
    """
    try:
        view.LookupParameter("Views_$Group").Set("00_EA's_Little Helper")
        view.LookupParameter("Views_$Series").Set("Warning Cleaning")

    except:

        EA_UTILITY.print_note( traceback.format_exc())

    t.Commit()

    uidoc.ActiveView = view



def create_view(view_name):
    desired_name = "EnneadTab Warning Cleaning View_" + view_name
    view = get_view_by_name(desired_name)
    if view is not None:
        return view
    print("####creating new axon view for " + view_name)
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


def random_pick():

    #print "doing randomg pick"
    # get all warnings
    all_warnings = doc.GetWarnings()

    #  shorten to warning s about wall and rm sp line overlap
    warnings = filter(lambda x: "One of them may be ignored when Revit finds room boundaries" in x.GetDescriptionText(), all_warnings)

    # pick random warning
    #print warnings
    warning = random.choice(warnings)
    #  get related wal and sp line
    error_els = warning.GetFailingElements()
    #bbox = doc.GetElement(error_els[0]).get_BoundingBox(doc.ActiveView)
    #min = bbox.Min
    #max = bbox.Max

    def is_smaller(A, B):
        return True

    min_pts = [doc.GetElement(item).get_BoundingBox(doc.ActiveView).Min for item in error_els]
    max_pts = [doc.GetElement(item).get_BoundingBox(doc.ActiveView).Max for item in error_els]


    min_X = min([pt.X for pt in min_pts])
    min_Y = min([pt.Y for pt in min_pts])
    min_Z = min([pt.Z for pt in min_pts])
    max_X = max([pt.X for pt in max_pts])
    max_Y = max([pt.Y for pt in max_pts])
    max_Z = max([pt.Z for pt in max_pts])

    """
    for item in error_els:
        bbox_current = doc.GetElement(item).get_BoundingBox(doc.ActiveView)
        min_current = bbox_current.Min
        max_current = bbox_current.Max
        if is_smaller(min_current, min):
            min = min_current
        if is_smaller(max, max_current):
            max = max_current

    bbox.Min = min
    bbox.Max = max
    """
    bbox = DB.BoundingBoxXYZ()
    bbox.Min = DB.XYZ(min_X, min_Y, min_Z)
    bbox.Max = DB.XYZ(max_X, max_Y, max_Z)
    #  show info on label show current warning count


    t = DB.Transaction(doc, "Random pick fixing pairs")
    t.Start()
    # set sectionbox around.
        # element.BoundingBox(document.ActiveView)
        # element.get_BoundingBox(document.ActiveView);

        #view3D.SetSectionBox(bbox)
    doc.ActiveView.SetSectionBox(bbox)




    #print "busy"
    t.Commit()
    try:
        for uiview in uidoc.GetOpenUIViews():
            if uiview.ViewId == doc.ActiveView.Id:
                uiview.ZoomToFit()
        uidoc.RefreshActiveView()
    except:
        print (traceback.format_exc())

# Create a subclass of IExternalEventHandler
class fix_warning_SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this

    # Execute method run in Revit API environment.
    def Execute(self, uiapp):
        try:
            try:
                self.do_this()
            except:
                print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"


# Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
# different functions using different handler class instances
simple_event_handler = fix_warning_SimpleEventHandler(random_pick)

# We now need to create the ExternalEvent
ext_event = ExternalEvent.Create(simple_event_handler)


# A simple WPF form used to call the ExternalEvent
class warning_fixer_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):

        #print "doing preaction"
        # get 3d view as current, set only show wall and sp line OST, not other curtain panles.

        # set EA helper



        try:
            make_3D_views_for_warning_cleaning()
        except:
            print (traceback.format_exc())



        return

    def __init__(self):
        self.pre_actions()

        xaml_file_name = "fix wanring_ModelessForm.xaml"
        WPFWindow.__init__(self, xaml_file_name)
        self.initial_count = get_current_warning_count()
        self.title_text.Text = "Get to fix wall/rm speration line overlap one at a time."
        self.sub_text_counter.Text = "Initial warning count when the tool started = {}".format(self.initial_count)
        self.sub_text.Text = "Current total warnings = {}".format(self.initial_count)

        self.primary_button.Content = "Randomly bring me to a warning area."
        self.Title = "EA_wall and rm seperation line overlap fixer."
        self.Width = 600
        self.Height = 400
        self.Show()



    def primary_button_click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        #print "primary button clicked"
        self.sub_text.Text = "Current total warnings = {}".format(get_current_warning_count())
        ext_event.Raise()
        # default_run_event.Raise()

    def close_button_click(self, sender, e):

        #print "close button clicked"
        self.Close()





################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !
    modeless_form = warning_fixer_ModelessForm()




