
from pyrevit import  EXEC_PARAMS, script

import EnneadTab
from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 
uiapp = UI.UIApplication(doc.Application)


@EnneadTab.ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    # if not EnneadTab.USER.is_SZ():
    #     return
    if doc.IsFamilyDocument:
        return
    
    EnneadTab.NOTIFICATION.duck_pop(main_text = "EnneaDuck dislikes CAD import!\nQuack!")
    options = ["I don't want a duck to tell me what to do! Just import CAD already!",
               "Ok, cancel 'Import CAD', I will use 'Link CAD' instead."]
    res = EnneadTab.REVIT.REVIT_FORMS.dialogue(main_text = "Are you sure you want to use CAD import instead of CAD link?",
                                                sub_text = "Imported CAD cannot be updated later.",
                                                options = options)
    if res == options[0]:
        args.Cancel = False
        EnneadTab.NOTIFICATION.duck_pop(main_text = "Naughty! Good luck finding your CAD later.")
    elif res == options[1]:
        EnneadTab.NOTIFICATION.messenger(main_text = "Linking CAD...")
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