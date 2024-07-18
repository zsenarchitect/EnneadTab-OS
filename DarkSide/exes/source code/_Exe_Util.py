import os
import traceback
import json
import math

ESOSYSTEM_FOLDER = "{}\Documents\EnneadTab Ecosystem".format(os.environ["USERPROFILE"])


def try_catch_error(func):

    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
            return out

        except PermissionError:
            print ("[WinError 32] The process cannot access the file because it is being used by another process")
        except EOFError:
            print ("fine.....")
        except Exception as e:
            error = traceback.format_exc()

            error += "\n\n######If you have EnneadTab UI window open, just close the window. Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
            error_file = get_file_in_dump_folder("error_log.txt")

            with open(error_file, "w") as f:
                f.write(error)

            username = os.environ["USERPROFILE"].split("\\")[-1]
            if username in ["szhang"]:
                os.startfile(error_file)

    return wrapper

def get_dump_folder():
    return "{}\Documents\EnneadTab Ecosystem\Dump".format(os.environ["USERPROFILE"])

def get_file_in_dump_folder(file_name):
    return "{}\{}".format(get_dump_folder(), file_name)

def read_json_as_dict_in_dump_folder(file_name):
    filepath = get_file_in_dump_folder(file_name)
    
    # return empty dict if file not exist
    if not os.path.exists(filepath):
        return {}
    # reads it back
    with open(filepath,"r") as f:
      dict = json.load(f)
    return dict





GLOBAL_SETTING_FILE = 'setting_{}.sexyDuck'.format(os.environ["USERPROFILE"].split("\\")[-1])

def get_setting(key, defaule_value=None):
    data = read_json_as_dict_in_dump_folder(GLOBAL_SETTING_FILE)
    return data.get(key, defaule_value)








