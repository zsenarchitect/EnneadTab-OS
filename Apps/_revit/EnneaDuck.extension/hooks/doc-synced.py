from pyrevit import EXEC_PARAMS
from Autodesk.Revit import DB # pyright: ignore


from pyrevit.coreutils import envvars
doc = EXEC_PARAMS.event_args.Document


from EnneadTab import ERROR_HANDLE, SOUND, LOG




def play_success_sound():
    file = 'sound_effect_mario_1up.wav'
    SOUND.play_sound(file)


@ERROR_HANDLE.try_catch_error(is_silent=True)
@LOG.log_revit
def doc_synced():
    play_success_sound()
    



#################################################################
if __name__ == "__main__":
    doc_synced()
