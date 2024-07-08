import json

import ENVIRONMENT
if ENVIRONMENT.is_Rhino_environment():
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs

import os
KNOWLEDGE_FILE = "{}\\knowledge_database.json".format(ENVIRONMENT.RHINO_FOLDER)
def register_alias_set():

    exisitng_alias = rs.AliasNames()
    with open(KNOWLEDGE_FILE, "r") as f:
        data = json.load(f)

    for root, dirs, files in os.walk(ENVIRONMENT.RHINO_FOLDER):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)

                if full_path.split("_rhino\\")[1] not in data.keys():
                    continue


                alias_list = data.get('__title__')
                if not isinstance(alias_list, list):
                    alias_list = [alias_list]

                for alias in alias_list:
                    if rs.IsAlias(alias) and "_rhino" not in exisitng_alias:
                        #Skip setting alias for {} due to overlapping names, this is usually becasue user has setup their personal alias that happen to be same name as EA ones
                        continue

                    # remove invalid alias due to folder change
                    if rs.IsAlias(alias):
                        current_macro = rs.AliasMacro(alias)
                        current_full_path = current_macro.split('_-RunPythonScript "')[1].split('"')[0]
                        if not os.path.exists(current_full_path):
                            rs.DeleteAlias(alias)
                        
                    script_content = '! _-RunPythonScript "{}"'.format(full_path)
                    if os.path.exists(full_path):
                        rs.AddAlias(alias, script_content)
