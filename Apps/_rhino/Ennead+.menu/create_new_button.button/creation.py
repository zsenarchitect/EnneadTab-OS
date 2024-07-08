import os



"""
this has the core function that is shared between Rhino version and IDE version
"""


TEMPLATE = """
__title__ = "{0}"
__doc__ = "{1}"


from EnneadTab import ERROR_HANDLE, LOG

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def {2}():
    {3}
if __name__ == "__main__":
    {2}()
"""
SAMPLE_PRINT_STATMENT ='print ("Placeholder func <{}> that does this:{}".format(__title__, __doc__))'

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
            print ("File with this click method exist.....check the folder.")
            return
            
    script_file = "{}\\{}_{}.py".format(button_folder, button_name, clicker )


    with open(script_file, "w") as f:
        f.write(script)
    
    os.startfile(script_file)






 

    