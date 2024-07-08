"""a json handler that store all the knowledge about current version
for the purpose of alis maker and documentation lookup."""

import uuid
import json
import os

KNOWLEDGE_FILE = "{}\\Apps\\_rhino\\knowledge_database.json".format(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

assert os.path.exists(KNOWLEDGE_FILE), "knowledge data file <{}> does not exist".format(KNOWLEDGE_FILE)



def process_path(path):
    if hasattr(path, "path"):
        path = path.path
    breaker = path.split("_rhino\\")
    if len(breaker) == 1:
        return path
    return breaker[1]


class KnowledgeHandler:
    _instances = {}
    _is_new_member = False  # Consider refactoring this logic


        
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
            script_path = process_path(script_path)
            icon_path = process_path(icon_path)
            self.initialized = True
            KnowledgeHandler._instances[script_path] = {
                "script":script_path,
                "icon":icon_path,
                "alias": global_vars.get("__title__"),
                "doc": global_vars.get("__doc__")
            }
            

    @classmethod
    def update_database(cls):

        
        if cls._is_new_member:
            with open(KNOWLEDGE_FILE, 'w') as f:
                json.dump(dict(cls._instances.items()), f, indent=4)
            cls._is_new_member = False  # Reset flag after update




if __name__ == "__main__":
    pass
