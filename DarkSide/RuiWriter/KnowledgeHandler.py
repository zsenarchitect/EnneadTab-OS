"""a json handler that store all the knowledge about current version
for the purpose of alis maker and documentation lookup."""

import uuid
import json
import os
from TabHandler import TabHandler


KNOWLEDGE_FILE = "{}\\Apps\\_rhino\\knowledge_database.sexyDuck".format(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

assert os.path.exists(KNOWLEDGE_FILE), "knowledge data file <{}> does not exist".format(KNOWLEDGE_FILE)



def process_path(path):
    # when searching for starup script there is never a icon, this path is designed to be None
    if path is None:
        return None
    if hasattr(path, "path"):
        path = path.path

    if "default_icon" in path:
        return None
    breaker = path.split("_rhino\\")
    if len(breaker) == 1:
        return path
    return breaker[1]

def get_tab_info(script_path):
    tab_name = None
    tab_icon = None
    key = ".tab" if ".tab" in script_path else ".menu"
    if key in script_path:
        tab_folder = script_path.split(key)[0] + key
        tab_name = os.path.basename(tab_folder)
        for f in os.listdir(tab_folder):
            if 'icon' in f:
                # make sure the file extension is either .png or .svg
                if f.endswith('.png') or f.endswith('.svg'):
                    icon_path = os.path.join(tab_folder, f)
                    tab_icon = process_path(icon_path)
                    break


        
    return tab_name, tab_icon

    
class KnowledgeHandler:
    _instances = {}
    _is_new_member = False  # Consider refactoring this logic

    @classmethod
    def init_database(cls):
        cls._instances = {}

        
    def __new__(cls, script_path, icon_path, global_vars):
        script_path = process_path(script_path)
        if script_path not in cls._instances:
            cls._is_new_member = True  # This flag might need rethinking
            instance = super().__new__(cls)
            cls._instances[script_path] = instance
            return instance
        return cls._instances[script_path]

    def __init__(self, script_path, icon_path, global_vars):
        if not hasattr(self, 'initialized'):  # Prevent double initialization
            
            tab_name, tab_icon = get_tab_info(script_path)

            
            script_path = process_path(script_path)
            icon_path = process_path(icon_path)
            self.initialized = True
            KnowledgeHandler._instances[script_path] = {
                "script":script_path,
                "icon":icon_path,
                "alias": global_vars.get("__title__"),
                "doc": global_vars.get("__doc__"),
                "tab": tab_name,
                "tab_icon":tab_icon
            }
            

    @classmethod
    def update_database(cls):

        
        if cls._is_new_member:
            with open(KNOWLEDGE_FILE, 'w') as f:
                json.dump(dict(cls._instances.items()), f, indent=4)
            cls._is_new_member = False  # Reset flag after update




if __name__ == "__main__":
    pass
