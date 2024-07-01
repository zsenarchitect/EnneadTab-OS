import os
import sys
parent_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append("{}\Source Codes\lib".format(parent_folder))
sys.path.append("{}\Source Codes\lib\Enneadtab".format(parent_folder))
from EnneadTab import NOTIFICATION


"""
this has the core function that is shared between Rhino version and IDE version
"""


TEMPLATE = """
__alias__ = "{0}"
__doc__ = "{1}"


def {2}():
    {3}

"""
SAMPLE_PRINT_STATMENT ='print ("Placeholder func <{}> that does this:{}".format(__alias__, __doc__))'

def make_button(tab_folder, button_name, is_left_click = True):
    print (tab_folder)
    print (button_name)
    clicker = "left" if is_left_click else "right" 
    better_alias = button_name.replace("_", " ").title().replace(" ", "")
    doc = "This button does {} when {} click". format(better_alias, clicker)
    script = TEMPLATE.format(better_alias, doc, button_name, SAMPLE_PRINT_STATMENT)
    print (script)

   

    button_folder = "{}\\{}.button".format(tab_folder, button_name)
    if not os.path.exists(button_folder):
        os.makedirs(button_folder)

    for file in os.listdir(button_folder):
        if file.endswith(".py") and clicker in file:
            NOTIFICATION.messenger("File with this click method exist.....check the folder.")
            return
            
    script_file = "{}\\{}_{}.py".format(button_folder, button_name, clicker )


    with open(script_file, "w") as f:
        f.write(script)
    
    os.startfile(script_file)






 

    