#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "A floating window that give you quick access to align tags horitiontally or verticaly after picking a ref tag."
__title__ = "Tag\nAligner"
__tip__ = True

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from System import EventHandler, Uri


from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import _HostApplication
from pyrevit import HOST_APP

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import IMAGE, ERROR_HANDLE, LOG
import traceback
from Autodesk.Revit import DB # pyright: ignore 


uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True






def test_elbow_straight(tag):
    #get archor position and elbow location, if thwo are same then it is straight line.
    if not tag.HasLeader:
        return False
    if tag.HasElbow:
        return False
    else:
        return True

def process_tag(ref_tag, bad_tag, is_V):
    def move_to_target_in_view(location,target_pt):
        if is_V:
            screen_vector = doc.ActiveView.UpDirection #!!!!this is great! use this!!!!!
        else:
            screen_vector = doc.ActiveView.RightDirection
        #print "this is unit x direction: {}".format(unit_x)
        pt_line = DB.Line.CreateUnbound(location, screen_vector)
        ped_pt = pt_line.Project(target_pt)#pependicular point with the project unbound line
        return ped_pt.XYZPoint

    temp_location = move_to_target_in_view(bad_tag.TagHeadPosition, ref_tag.TagHeadPosition)
    try:
        bad_tag.TagHeadPosition = temp_location
    except Exception as e:
        #print (e)
        #print "Tag with no leaders cannot have tag head outside the host. Will try to add leader for you."
        bad_tag.HasLeader = True
        bad_tag.TagHeadPosition = temp_location


    try:
        temp_location = move_to_target_in_view(bad_tag.LeaderElbow,ref_tag.LeaderElbow)
        bad_tag.LeaderElbow = temp_location
    except:
        if test_elbow_straight(bad_tag):
            pass
            #print "Elbow is straight, no elbow point for {}. The blbow move will be ignored".format(el.Id)

        elif bad_tag.HasLeader == False:
            #print "No leader for this element:{}. Leader moves will be ignored.".format(el.Id)
            pass
        else:
            #print "Elbow move fails for this element:{}".format(el.Id)
            pass


@ERROR_HANDLE.try_catch_error()
def align_tags(ref_tag, bad_tags, is_V):

    t = DB.Transaction(doc, "tag align")
    t.Start()
    map(lambda x:process_tag(ref_tag, x, is_V), bad_tags)
    t.Commit()




# Create a subclass of IExternalEventHandler
class tag_align_SimpleEventHandler(IExternalEventHandler):
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
class TagAligner(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.simple_event_handler = tag_align_SimpleEventHandler(align_tags)

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

        xaml_file_name = "TagAligner.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Tag Aligner"

        self.sub_text.Text = "Pick reference tag and align many tags toward it."


        self.Title = "EnneadTab TagAlign UI"

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)

        self.ref_tag = None
        self.hostapp = HOST_APP#_HostApplication(__revit__)
        if self.hostapp.is_newer_than(version = 2023, or_equal = True):
            from Autodesk.Revit.UI.Events import SelectionChangedEventArgs
            __revit__.SelectionChanged += EventHandler[SelectionChangedEventArgs](self.selection_update_event_handler_function)
        self.Show()


    @ERROR_HANDLE.try_catch_error()
    def selection_update_event_handler_function(self,sender, args):


        selection_ids = list(args.GetSelectedElements ())
        #print selection_ids
        #for x in selection_ids:
            #print x.IntegerValue
            #print doc.GetElement(DB.ElementId(x.IntegerValue))
        #return selection_ids
        selection = [doc.GetElement(DB.ElementId(x.IntegerValue)) for x in selection_ids]
        #print 999
        #print selection
        note = ""
        for x in selection:
            if hasattr(x, "Category"):
                if x.Category is None:
                    continue
                note += "{}\n".format(x.Category.Name)
            else:
                note += "{}\n".format(x)
        self.debug_textbox.Text = note

    @ERROR_HANDLE.try_catch_error()
    def pick_ref_tag_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        selection_ids = uidoc.Selection.GetElementIds ()
        if len( selection_ids) == 0:
            self.debug_textbox.Text = "Nothing selected."
            return


        selection = [doc.GetElement(x) for x in selection_ids]

        selection = filter(lambda x: "tag" in x.Category.Name.lower(), selection )
        if len( selection) != 1:
            self.debug_textbox.Text = "Need exact one tag as reference."
            return
        self.ref_tag = selection[0]
        self.debug_textbox.Text = "Ref tag captured. {}".format(self.ref_tag.Id)



    def clear_ref_tag_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.debug_textbox.Text = "No ref tag selected."
        self.ref_tag = None


    def align_H_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click(is_V = False)

    def align_V_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.generic_click(is_V = True)

    @property
    def bad_tags(self):
        selection_ids = uidoc.Selection.GetElementIds ()

        selection = [doc.GetElement(x) for x in selection_ids]
        selection = filter(lambda x: x.Category, selection )
        selection = filter(lambda x: x.Category.Name, selection )
        selection = filter(lambda x: "tag" in x.Category.Name.lower(), selection )
        return selection

    @ERROR_HANDLE.try_catch_error()
    def generic_click(self, is_V):
        #print "Clicking " + keyword
        if not self.ref_tag:
            self.debug_textbox.Text = "There is no ref tag captured."
            return


        self.simple_event_handler.kwargs = self.ref_tag, self.bad_tags, is_V
        self.ext_event.Raise()
        res = self.simple_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"


    @ERROR_HANDLE.try_catch_error()
    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()
        if self.hostapp.is_newer_than(version = 2023, or_equal = True):
            from Autodesk.Revit.UI.Events import SelectionChangedEventArgs
            __revit__.SelectionChanged -= EventHandler[SelectionChangedEventArgs](self.selection_update_event_handler_function)

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()






@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    TagAligner()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()


