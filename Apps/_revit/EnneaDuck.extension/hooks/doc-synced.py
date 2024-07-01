from pyrevit import EXEC_PARAMS
from Autodesk.Revit import DB # pyright: ignore


from pyrevit.coreutils import envvars
doc = EXEC_PARAMS.event_args.Document


from EnneadTab import ERROR_HANDLE, SOUND, LOG




def play_success_sound():
    file = 'sound_effect_mario_1up.wav'
    SOUND.play_sound(file)


@LOG.log
@ERROR_HANDLE.try_catch_error_silently
def main():
    play_success_sound()
    



#################################################################
if __name__ == "__main__":
    main()
