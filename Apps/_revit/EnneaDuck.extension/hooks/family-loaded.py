
"""
store session script data to a temp file
https://pyrevit.readthedocs.io/en/latest/pyrevit/coreutils/appdata.html


share parameter between script
https://pyrevit.readthedocs.io/en/latest/pyrevit/coreutils/envvars.html
"""
from pyrevit import script
from pyrevit import EXEC_PARAMS


#from pyrevit.coreutils import appdata
import pickle
from pyrevit.coreutils import envvars
import time

from EnneadTab import ERROR_HANDLE, SOUND, NOTIFICATION, TIME
from EnneadTab.REVIT import REVIT_FORMS

def get_subc(category):
    temp = []
    for c in category:
        for sub_c in c.SubCategories:
            temp.append("[{0}]--->[{1}]".format(c.Name , sub_c.Name))
    return temp


def difference_list(L1, L2):
    temp = []
    temp.extend( list(set(L1) - set(L2)) )
    temp.extend( list(set(L2) - set(L1)) )
    return temp

@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():
    SOUND.play_sound("sound_effect_mario_coin.wav")


    doc = EXEC_PARAMS.event_args.Document
    if doc.IsFamilyDocument:
        """
        lines = ["Family loaded.",
                "Loaded into {}".format(doc.Title)]
        EA_UTILITY.random_speak(lines)
        """
        return

    start_time = envvars.get_pyrevit_env_var("FAMILY_LOAD_BEGIN")
    time_pass = time.time() - start_time
    NOTIFICATION.messenger("Family load finished!!\n<{}> Uses {}".format(EXEC_PARAMS.event_args.FamilyName, TIME.get_readable_time(time_pass)))

    """
    lines = ["Family loaded in {} mins".format(int(time_pass/60)),
            "Loaded into {}".format(doc.Title)]
    EA_UTILITY.random_speak(lines)
    """


    #output.print_md("this loaded script")

    datafile = script.get_instance_data_file("sub_c_list")
    #print datafile

    f = open(datafile, 'r')
    old_sub_c_list  = pickle.load(f)
    f.close()
    #print old_sub_c_list

    all_Cs = doc.Settings.Categories
    current_sub_c_list = get_subc(all_Cs)
    #print current_sub_c_list

    #print "\n\n\n\n**************************"
    new_sub_c_list =  difference_list(current_sub_c_list, old_sub_c_list)

    """
    output = script.get_output()
    #output.self_destruct(150)
    output.print_md("#The following subCategory(s) brought to the project does not exist before family loaded. Please take screenshot and use Ideate tool to manage object style properly.")
    for item in new_sub_c_list:
        print(item)
    """

    if len(new_sub_c_list) == 0:
        return

    display_text = "Ennead Alert:\nThe following new subCategory(s) are brought to the project by loading the family.\n\n"
    for item in new_sub_c_list:
        display_text += "{0} \n".format(item)
    sub_display_text = "It happens when new sub-category is created intentionally, but also when you load a family:\n\n--from other project;\n--from manufacture website;\n--with a typo to an existing sub-category name.\n\nIf this is unintensional, please take notes and use Ideate 'StyleManager' tool to manage object style later."

    REVIT_FORMS.notification(main_text = display_text,
                            sub_text = sub_display_text,
                            self_destruct = 5,
                            window_width = 650)

#############  main    ###########
if __name__ == "__main__":

    main()
