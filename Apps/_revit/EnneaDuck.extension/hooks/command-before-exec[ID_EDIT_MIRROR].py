
from pyrevit import  EXEC_PARAMS, script
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import NOTIFICATION, ERROR_HANDLE
from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 
uiapp = UI.UIApplication(doc.Application)
# uiapp.PostCommand(args.CommandId)


@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    uidoc = UI.UIDocument(doc)
    selection_ids = uidoc.Selection.GetElementIds()
    selection = [doc.GetElement(x) for x in selection_ids]
    for x in selection:
        if not x.Category:
            continue
        if "group" in x.Category.Name.lower():
            NOTIFICATION.messenger("Mirroring group might lead to corrupted group later.")
            return
 
############################
output = script.get_output()
output.close_others()


if __name__ == '__main__':
    main()