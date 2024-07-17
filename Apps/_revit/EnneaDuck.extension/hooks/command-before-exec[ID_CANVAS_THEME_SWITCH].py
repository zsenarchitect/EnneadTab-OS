
# from pyrevit import  EXEC_PARAMS, script

from EnneadTab import ERROR_HANDLE, NOTIFICATION, SOUNDS
# from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
# args = EXEC_PARAMS.event_args
# doc = args.ActiveDocument 
# uidoc = UI.UIDocument(doc)
# uiapp = UI.UIApplication(doc.Application)
# uiapp.PostCommand(args.CommandId)

@ERROR_HANDLE.try_catch_error_silently
def main():
    
    if UI.UIThemeManager.CurrentCanvasTheme == UI.UITheme.Dark:
        NOTIFICATION.duck_pop("Wake up!!!")
    else:
        NOTIFICATION.duck_pop("Go to sleep!!!")
    
    SOUNDS.play_sound("sound effect_notification new.wav")
    
############################


if __name__ == '__main__':
    main()