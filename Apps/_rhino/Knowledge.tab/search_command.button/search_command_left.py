__alias__ = "SearchCommand"
__doc__ = "Learn all the buttons functions."


import os
from Duckitect import PARSER
from Duckitect.RHINO import RHINO_ALIAS

# this is for the interactive search UI that gives the detail explanation of evrything
def get_all_data():
    


    
    toolbar_folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data = {}

    for root, dirs, files in os.walk(toolbar_folder):
        for file in files:
            if not file.endswith(".py"):
                continue
            
            file_path = os.path.join(root, file)
            script_data = PARSER.extract_global_variables(file_path)

            alias = script_data.get('__alias__')
            if not alias:
                continue

            if not isinstance(alias, list):
                alias = [alias]

            for a in alias:
                data[a] = {
                    "script_path": file_path,
                    "doc": script_data.get('__doc__'),
                    "icon": "{}\\icon.png".format(root),
                    "is_left": "_left" in file,
                    "button_name": "123",
                    "button_icon": 123,
                    "tab_name": "123",
                    "tab_icon": 123
                           }
            
                
    return data         


def search_command():
    RHINO_ALIAS.register_alias_set()
    print ("Placeholder func <{}> that does this:{}".format(__alias__, __doc__))

