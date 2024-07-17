import json

import ENVIRONMENT
if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs

import os
KNOWLEDGE_FILE = "{}\\knowledge_database.json".format(ENVIRONMENT.RHINO_FOLDER)


def remove_invalid_alias():
    exisitng_alias = rs.AliasNames()
    for alias in exisitng_alias:
        exisiting_macro = rs.AliasMacro(alias)
        if "RunPythonScript" not in exisiting_macro:
            continue
        exisiting_full_path = exisiting_macro.split('_-RunPythonScript "')[1].split('"')[0]
        if not os.path.exists(exisiting_full_path):
            rs.DeleteAlias(alias)

def register_alias_set():
    remove_invalid_alias()
    exisitng_alias = rs.AliasNames()
    
            
    with open(KNOWLEDGE_FILE, "r") as f:
        data = json.load(f)

    for root, dirs, files in os.walk(ENVIRONMENT.RHINO_FOLDER):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                # print (full_path)
                # print(full_path.split("_rhino\\")[1])

                if full_path.split("_rhino\\")[1] not in data.keys():
                    continue
                


                alias_list = data.get(full_path.split("_rhino\\")[1]).get('alias')


                if not isinstance(alias_list, list):
                    alias_list = [alias_list]

                for alias in alias_list:
                    if not alias:
                        continue

                    if rs.IsAlias(alias) and "_rhino" not in exisitng_alias:
                        #Skip setting alias for {} due to overlapping names, this is usually becasue user has setup their personal alias that happen to be same name as EA ones
                        continue


                    script_content = '! _-RunPythonScript "{}"'.format(full_path)
                    if os.path.exists(full_path):
                        if alias == alias.upper():
                            rs.AddAlias(alias, script_content)
                        else:
                            rs.AddAlias("EA_" + alias, script_content)

