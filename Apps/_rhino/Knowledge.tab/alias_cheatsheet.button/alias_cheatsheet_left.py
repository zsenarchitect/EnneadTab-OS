
__alias__ = "AliasCheatsheet"
__doc__ = "Learn about ALL the EnneadTab alias."

import os
from EnneadTab import PARSER, OUTPUT
from EnneadTab.RHINO import RHINO_ALIAS

def alias_cheatsheet():
    RHINO_ALIAS.register_alias_set()
    
    toolbar_folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    output = OUTPUT.get_output()

    for root, dirs, files in os.walk(toolbar_folder):
        if root.endswith(".tab"):
            tab_name = os.path.basename(root).replace(".tab", "")


            output.write("-------[{}]--------".format(tab_name),OUTPUT.Style.Title)

        if root.endswith(".button"):
            button_name = os.path.basename(root).replace(".button", "")

            
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
                output.write("[{}]:{}".format(a, script_data.get('__doc__')))

            output.write("\n\n")
        output.insert_division()

    output.plot()
