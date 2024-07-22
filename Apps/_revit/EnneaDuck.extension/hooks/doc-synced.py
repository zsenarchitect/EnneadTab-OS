from pyrevit import EXEC_PARAMS
from Autodesk.Revit import DB # pyright: ignore

from pyrevit.coreutils import envvars
doc = EXEC_PARAMS.event_args.Document


import proDUCKtion # pyright: ignore 
from EnneadTab import ERROR_HANDLE, SOUND, LOG
from EnneadTab.REVIT import REVIT_SYNC
__title__ = "Doc Synced Hook"



def play_success_sound():
    file = 'sound_effect_mario_1up.wav'
    SOUND.play_sound(file)

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error(is_silent=True)
def doc_synced():
    play_success_sound()

    REVIT_SYNC.update_last_sync_data_file(doc)
    



#################################################################
if __name__ == "__main__":
    doc_synced()
