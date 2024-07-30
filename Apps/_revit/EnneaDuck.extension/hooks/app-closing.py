#from pyrevit import script
#from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ERROR_HANDLE, SOUND

def play_closing_sound():
    file = "sound_effect_mario_game_over.wav"
    SOUND.play_sound(file)

@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    #general_annoucement()

    play_closing_sound()
################### main code below ###############
if __name__ == "__main__":
    main()