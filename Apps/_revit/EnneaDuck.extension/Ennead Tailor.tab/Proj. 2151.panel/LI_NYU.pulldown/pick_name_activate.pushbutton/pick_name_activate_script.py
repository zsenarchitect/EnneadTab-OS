#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Pick Name(DO NOT USE)"

from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
from Autodesk.Revit.UI.Events import SelectionChangedEventArgs
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from System import EventHandler, Uri
                
@EnneadTab.ERROR_HANDLE.try_catch_error
def pick_name_activate():
    print(__revit__.SelectionChanged)
    for item in dir(__revit__.SelectionChanged):
        print(item)
    print(__revit__.SelectionChanged.Event)
    
    
    option = ["Activate","DeActivate"]
    res = EnneadTab.REVIT.REVIT_FORMS.dialogue(options = option)
    if not res:
        return
    if res == option[0]:
        __revit__.SelectionChanged += EventHandler[SelectionChangedEventArgs](event_handler_function)      
        EnneadTab.NOTIFICATION.messenger(main_text = "Name Picker Enabled!\nNow select your pill shape...")
    else:
        __revit__.SelectionChanged -= EventHandler[SelectionChangedEventArgs](event_handler_function)  
        EnneadTab.NOTIFICATION.messenger(main_text = "Name picker Disabled.")


    """
    t = DB.Transaction(doc, __title__)
    t.Start()
    $$$$$$$$$$$$$$$$$$$
    t.Commit()
    """
@EnneadTab.ERROR_HANDLE.try_catch_error
def event_handler_function(sender, args):
    import sys
    sys.path.append("L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Published\\ENNEAD.extension\\lib")
    import EnneadTab
    from pyrevit import forms
    from Autodesk.Revit import DB # pyright: ignore 
    # from Autodesk.Revit import UI # pyright: ignore
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
    from Autodesk.Revit.UI.Events import SelectionChangedEventArgs
    from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
    from System import EventHandler, Uri
    """
    have to wrap entire ting in try catch becasue G keep forgetting to close/unsubscribe who did that properly so there are always error emaill
    """
    
    selection_ids = list(args.GetSelectedElements ())
    if len (selection_ids) == 0:
        return 
    
    if len (selection_ids) != 1:
        EnneadTab.NOTIFICATION.messenger(main_text = "Select one and only one pill shape")
        return
    
    element = doc.GetElement(selection_ids[0])
    if not EnneadTab.REVIT.REVIT_FORMS.is_changable(element):
        EnneadTab.NOTIFICATION.messenger(main_text = "You do not have permission to edit it.")
        return
    
    
    if not hasattr(element, "Symbol") or not element.Symbol.FamilyName.lower().startswith( "DTL_Healthcare_Planning_Section Bubble".lower()):
        EnneadTab.NOTIFICATION.messenger(main_text = "This tool only work with the pill shape")
        return
    
    
    color_schemes = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_ColorFillSchema).WhereElementIsNotElementType().ToElements()
    def scheme_name(x):
        cate_name = DB.Category.GetCategory(doc, x.CategoryId).Name
        return "[{}]: {}".format(cate_name, x.Name)
    color_scheme = filter(lambda x: scheme_name(x) == "[Areas]: Department Category", color_schemes)[0]

    names = [entry.GetStringValue()  for entry in color_scheme.GetEntries()]
         
    name = forms.SelectFromList.show(sorted(names),
                                    multiselect=False)
    if not name:
        return
    # EnneadTab.NOTIFICATION.messenger(main_text = name)
    name = EnneadTab.TEXT.wrapped_text(name)


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

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def action(element, name):
        t = DB.Transaction(doc, __title__)
        t.Start()
        element.LookupParameter("bubble_diagram_label").Set(name)
        
        t.Commit()
    
    
    simple_event_handler = SimpleEventHandler(action)
    ext_event = ExternalEvent.Create(simple_event_handler)
    simple_event_handler.kwargs = element, name
    ext_event.Raise()


        


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    pick_name_activate()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)


