"""need to impletemnt this becasue ever changing guid in rui make it hard to collabrate over git,,
, it wil assume massive change everytime.
so this make guid more stable.


for the benefit of comtinous sharing work, i think
it is better to NOT generate new guid everytime it create a new rui.

so make a json that store the exsiting path and guid.
This script has the class to handle this logic so unless we are 
making change to layout, any existing content will use the same
guid so there will be less chance of git conflict



in memory, load up json and only gnerate new guid and store it when"""

import uuid
import json
import os

DATA_FILE = "{}\\guid_database.json".format(os.path.dirname(os.path.realpath(__file__)))

assert os.path.exists(DATA_FILE), "guid data file does not exist"



def process_path(path):
    breaker = path.split("_rhino\\")
    if len(breaker) == 1:
        return path
    return breaker[1]


class GuidHandler:
    _instances = {}
    _is_new_member = False  # Consider refactoring this logic

    @classmethod
    def init_database(cls):
        with open (DATA_FILE, 'r') as f:
            storage = json.load(f)
            
        cls._instances = {k:GuidHandler(k, existing_guid = v) for k,v in storage.items()}

        
    def __new__(cls, path, existing_guid=None):
        path = process_path(path)
        if path not in cls._instances:
            cls._is_new_member = True  # This flag might need rethinking
            instance = super().__new__(cls)
            cls._instances[path] = instance
            return instance
        return cls._instances[path]

    def __init__(self, path, existing_guid=None):
        if not hasattr(self, 'initialized'):  # Prevent double initialization
            path = process_path(path)
            self.path = path
            self.guid = existing_guid if existing_guid else str(uuid.uuid4())
            self.initialized = True

    @classmethod
    def update_database(cls):
        if cls._is_new_member:
            storage = {k: v.guid for k, v in cls._instances.items()}
            with open(DATA_FILE, 'w') as f:
                json.dump(storage, f, indent=4)
            cls._is_new_member = False  # Reset flag after update




if __name__ == "__main__":
    pass
    # GuidHandler.init_database()
    # a = GuidHandler("EnneadTab-for-Rhino\\a")
    # b = GuidHandler("EnneadTab-for-Rhino\\a")
    # print(a.guid)
    # print(b.guid)
    # GuidHandler.update_database()
    # print(GuidHandler._instances)
    # c = GuidHandler("EnneadTab-for-Rhino\\c")
    # print(c.guid)
    # GuidHandler.update_database()
    # print(GuidHandler._instances)
    # d = GuidHandler("EnneadTab-for-Rhino\\anything")
    # print(d.guid)
    # GuidHandler.update_database()
    # print(GuidHandler._instances)
        