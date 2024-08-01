
"""sometimessssss a exernal event does not need a modeless form, that is why this class is a seperated piece"""

import traceback
try:
    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore


    from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent # pyright: ignore
    from Autodesk.Revit.Exceptions import InvalidOperationException # pyright: ignore
    REF_CLASS_IExternalEventHandler = IExternalEventHandler
except:
    REF_CLASS_IExternalEventHandler = object

EVENT_MARKER_KEY="ENNEADTAB_EVENT_MARKER" 
import ERROR_HANDLE


# Create a subclass of IExternalEventHandler
class SimpleEventHandler(REF_CLASS_IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.args = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):
        try:
            try:
                #print "try to do event handler func"
                event_mark_start()
                self.OUT = self.do_this(*self.args)
                event_mark_end()

            except:
                print ("event runner failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"
    
    
    
class ExternalEventRunner:
    
    def __init__(self, *funcs):
        if len(funcs) == 0:
            print("here is no funcs")
            return
        for func in funcs:
            original_func = getattr(func, 'original_function', func)  # Use the original function if available
            handler = SimpleEventHandler(original_func)
            setattr(self, "simple_event_handler_{}".format(original_func.__name__), handler)
            setattr(self, "ext_event_{}".format(original_func.__name__), ExternalEvent.Create(handler))
            # print (original_func.__name__ + " has been regiested!!!!!!!!")
            
    @ERROR_HANDLE.try_catch_error(is_silent=True)
    def run(self, func_name, *args):
        event = getattr(self, "ext_event_{}".format(func_name))
        handler = getattr(self, "simple_event_handler_{}".format(func_name))
        
        
        handler.args = args
        event.Raise()
        
        wait_event()
        
        return handler.OUT





#TO-DO: the idea behinds those two mark funcs is to resolve the issue that modeless form func once passed cannot pass the res back.
def event_mark_start():
    return
    os. evn[MARKER] = True

def event_mark_end():
    return
    os. evn[MARKER] = False

def wait_event():
    return
    max_wait=15
    while True:
        if is_event_done():
            return 

        max_wait -= 1
        
        if max_wait<0:
            return 