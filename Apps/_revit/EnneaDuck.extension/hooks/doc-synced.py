from pyrevit import EXEC_PARAMS
from Autodesk.Revit import DB # pyright: ignore


from pyrevit.coreutils import envvars
doc = EXEC_PARAMS.event_args.Document


from Duckitect import ERROR_HANDLE, SOUND, LOG
__title__ = "Doc Synced Hook"



def play_success_sound():
    file = 'sound_effect_mario_1up.wav'
    SOUND.play_sound(file)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error(is_silent=True)
def doc_synced():
    play_success_sound()
    



#################################################################
if __name__ == "__main__":
    doc_synced()
