
# from pyrevit import  EXEC_PARAMS, script

import random
import time
from EnneadTab import ERROR_HANDLE, NOTIFICATION, SOUND
# from Autodesk.Revit import DB # pyright: ignore
# from Autodesk.Revit import UI # pyright: ignore
# args = EXEC_PARAMS.event_args
# doc = args.ActiveDocument 
# uidoc = UI.UIDocument(doc)
# uiapp = UI.UIApplication(doc.Application)
# uiapp.PostCommand(args.CommandId)

@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    notes = ["not recommended.",
             "frowned upon.",
             "ridiculous.",
             "will backfire in the future."]
    NOTIFICATION.messenger("Overriding element per view is allowed but {}".format(random.Random(time.time()).choice(notes)))
    SOUND.play_sound("meme_oof.wav")
    
    
############################


if __name__ == '__main__':
    main()