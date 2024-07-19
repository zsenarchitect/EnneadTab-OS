
from pyrevit import  EXEC_PARAMS, script

from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_FORMS
from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 
uiapp = UI.UIApplication(doc.Application)
# uiapp.PostCommand(args.CommandId)


@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    # if not EnneadTab.USER.IS_DEVELOPER:
    #     return
    if doc.IsFamilyDocument:
        return
    
    NOTIFICATION.duck_pop(main_text = "EnneaDuck dislikes in-place family!\nYou are in big trouble! Quack!")
    options = ["I don't want a duck to tell me what to do! I must use in-place family today!",
               "Ok, cancel 'In-Place Family', I will use loadable family instead."]
    res = REVIT_FORMS.dialogue(main_text = "Are you sure you want to use in-place family here?",
                                                sub_text = "In-place family has more cons than pros, if you are not sure, you can reach out to any Applied Computing Member for help.",
                                                options = options)
    if res == options[0]:
        args.Cancel = False
        
        
    elif res == options[1]:
        args.Cancel = True
    else:
        # if user click 'X' to close window
        args.Cancel = True
    
############################
output = script.get_output()
output.close_others()


if __name__ == '__main__':
    main()