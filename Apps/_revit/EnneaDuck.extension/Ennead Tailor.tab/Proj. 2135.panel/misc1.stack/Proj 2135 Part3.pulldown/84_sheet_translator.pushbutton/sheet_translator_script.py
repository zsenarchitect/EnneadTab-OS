#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "DO NOT USE, use newer AI translator"
__title__ = "84_sheet_translator"

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #

import traceback
from Autodesk.Revit import DB # pyright: ignore 
import random
# from Autodesk.Revit import UI # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
__persistentengine__ = True






def rename_sheet():

    global SHEET, USER_INPUT
    if not SHEET:
        return
    t = DB.Transaction(doc, "Update sheet trnalstion")
    t.Start()

    SHEET.LookupParameter("MC_$Translate").Set(USER_INPUT)
    t.Commit()
    return
    try:
        for uiview in uidoc.GetOpenUIViews():
            if uiview.ViewId == doc.ActiveView.Id:
                uiview.ZoomToFit()
        uidoc.RefreshActiveView()
    except:
        print (traceback.format_exc())

# Create a subclass of IExternalEventHandler
class rename_sheet_SimpleEventHandler(IExternalEventHandler):
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
simple_event_handler = rename_sheet_SimpleEventHandler(rename_sheet)

# We now need to create the ExternalEvent
ext_event = ExternalEvent.Create(simple_event_handler)


# A simple WPF form used to call the ExternalEvent
class rename_sheet_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def __init__(self):

        xaml_file_name = "sheet translator_ModelessForm.xaml"
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "Sheet Translator"
        self.sub_text_current_sheet_num.Text = "123"
        self.sub_text_current_sheet_name.Text = "ABC"

        self.textbox_translation_input.Text = "type in here"

        self.primary_button.Content = "Find a sheet without translation yet"
        self.second_button.Content = "Update sheet translation per textbox."

        self.Title = "EA_Sheet Translator."
        self.Width = 600
        self.Height = 400
        self.Show()


    def get_new_sheet(self):
        all_sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()

        print(all_sheets)
        def is_empty_translation(sheet):
            para =  sheet.LookupParameter("MC_$Translate")
            if not para:
                return False
            if para.AsString() == "":
                return True
            return False

        sheets = filter(is_empty_translation, all_sheets)
        sheets.sort(key = lambda x:x.SheetNumber)
        print(sheets)
        try:
            sheet = sheet[0]
        except Exception as e:
            print(str(e))
            return


        self.sub_text_current_sheet_num.Text = sheet.SheetNumber
        self.sub_text_current_sheet_nname.Text = sheet.LookupParameter("Sheet Name").AsString()
        self.textbox_translation_input.Text = "type in here"
        self.sheet = sheet


    def primary_button_click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        #print "primary button clicked"
        self.get_new_sheet()
        # default_run_event.Raise()


    def second_button_click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        #print "primary button clicked"
        global SHEET, USER_INPUT
        SHEET = self.sheet
        USER_INPUT = self.textbox_translation_input.Text
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
    modeless_form = rename_sheet_ModelessForm()
