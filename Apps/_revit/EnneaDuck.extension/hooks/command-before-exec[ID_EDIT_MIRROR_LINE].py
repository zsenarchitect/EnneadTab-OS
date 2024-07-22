
from pyrevit import  EXEC_PARAMS, script
import os

import proDUCKtion # pyright: ignore 
from EnneadTab import ERROR_HANDLE

from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore  
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 
uiapp = UI.UIApplication(doc.Application)
# uiapp.PostCommand(args.CommandId)


@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():

    import imp
    module_name = "command-before-exec[ID_EDIT_MIRROR]"
    module_path = "{}\\{}.py".format(os.path.realpath(os.path.dirname(__file__)), module_name)
    module = imp.load_source(module_name, module_path)
    module.main()
############################
output = script.get_output()
output.close_others()


if __name__ == '__main__':
    main()