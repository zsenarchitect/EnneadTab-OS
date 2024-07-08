
import ENVIRONMENT
if ENVIRONMENT.is_Rhino_environment():
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs

import os
# import sys
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import PARSER

def register_alias_set():

    exisitng_alias = rs.AliasNames()

    for root, dirs, files in os.walk(ENVIRONMENT.RHINO_FOLDER):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)

                data = PARSER.extract_global_variables(full_path)

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
