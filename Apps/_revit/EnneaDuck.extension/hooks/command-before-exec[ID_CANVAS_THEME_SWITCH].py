
# from pyrevit import  EXEC_PARAMS, script

from EnneadTab import ERROR_HANDLE, NOTIFICATION, SOUND
# from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
# args = EXEC_PARAMS.event_args
# doc = args.ActiveDocument 
# uidoc = UI.UIDocument(doc)
# uiapp = UI.UIApplication(doc.Application)
# uiapp.PostCommand(args.CommandId)

@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    
    if UI.UIThemeManager.CurrentCanvasTheme == UI.UITheme.Dark:
        NOTIFICATION.duck_pop("Wake up!!!")
    else:
        NOTIFICATION.duck_pop("Go to sleep!!!")
    
    SOUND.play_sound("sound_effect_notification_new.wav")
    
############################


if __name__ == '__main__':
    main()