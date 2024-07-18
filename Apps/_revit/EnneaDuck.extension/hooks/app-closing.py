#from pyrevit import script
#from Autodesk.Revit import DB # pyright: ignore
from Autodesk.Revit import UI # pyright: ignore

import EnneadTab


def general_annoucement():
    output = script.get_output()
    output.print_md("**SH team please note that Autodesk will maintain server on July 10, this might overlap with your working hour on Monday.**")
    output.print_image(r'file:\\L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\lib\annoucement\revit maintain.png')
    EA_UTILITY.dialogue(main_text = "SH team please note that Autodesk will maintain server on July 10, 1-6pm ET, this might overlap with your working hour on Monday.", sub_text = "Check with your team ACE to plan ahead.", footer_link = "https://health.autodesk.com/incidents/9m442dbcmt72",
    footer_text = "Autodesk Health")


def play_closing_sound():
    file = "sound_effect_mario_game_over.wav"
    EnneadTab.SOUND.play_sound(file)

@EnneadTab.ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    #general_annoucement()

    play_closing_sound()
################### main code below ###############
if __name__ == "__main__":
    main()