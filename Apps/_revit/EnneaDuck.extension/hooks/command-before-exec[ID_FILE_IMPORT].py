
from pyrevit import  EXEC_PARAMS, script

from EnneadTab import NOTIFICATION, ERROR_HANDLE
from EnneadTab.REVIT import REVIT_FORMS
from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 
uiapp = UI.UIApplication(doc.Application)


@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    # if not USER.IS_DEVELOPER:
    #     return
    if doc.IsFamilyDocument:
        return
    
    NOTIFICATION.duck_pop(main_text = "EnneaDuck dislikes CAD import!\nQuack!")
    options = ["I don't want a duck to tell me what to do! Just import CAD already!",
               "Ok, cancel 'Import CAD', I will use 'Link CAD' instead."]
    res = REVIT_FORMS.dialogue(main_text = "Are you sure you want to use CAD import instead of CAD link?",
                                                sub_text = "Imported CAD cannot be updated later.",
                                                options = options)
    if res == options[0]:
        args.Cancel = False
        NOTIFICATION.duck_pop(main_text = "Naughty! Good luck finding your CAD later.")
    elif res == options[1]:
        NOTIFICATION.messenger(main_text = "Linking CAD...")
        command_id = UI.RevitCommandId.LookupPostableCommandId(UI.PostableCommand.LinkCAD)
        uiapp.PostCommand(command_id)
        args.Cancel = True
    else:
        # if user click 'X' to close window
        args.Cancel = True
        
    # print (args.Cancel)
    
                                        
############################
output = script.get_output()
output.close_others()


if __name__ == '__main__':
    main()