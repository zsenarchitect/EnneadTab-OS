
import os
import time
import json

import USER
import ENVIRONMENT
import TIME
import FOLDER
import USER




from contextlib import contextmanager

@contextmanager
def log_usage(func,*args):
    t_start = time.time()
    res = func(*args)
    yield res
    t_end = time.time()
    duration = TIME.get_readable_time(t_end - t_start)
    with open(get_log_file(), "a") as f:
        f.writelines('\nRun at {}'.format(TIME.get_formatted_time(t_start)))
        f.writelines('\nDuration: {}'.format(duration))
        f.writelines('\nFunction name: {}'.format(func.__name__))
        f.writelines('\nArguments: {}'.format(args))
        f.writelines('\nResult: {}'.format(res))


# with log_usage(get_log_file()) as f:
#     f.writelines('\nYang is writing!')

    


        
def get_log_folder():

    if "log_folder" not in locals():
        log_folder = FOLDER.get_EA_dump_folder_file("log")
        FOLDER.secure_folder(log_folder)
    return log_folder


def get_log_file(user_name = None):
    log_folder = get_log_folder()
    if not user_name:
        user_name = USER.USER_NAME
    return "{}\{}.json".format(log_folder, user_name)

def log(script_path, func_name_as_record):
    def decorator(func):
        def wrapper(*args, **kwargs):
            log_file = get_log_file()


            if not os.path.exists(log_file):
                with open(log_file, "w") as f:
                    data = dict()
                    data["personal_data"] = {"name": USER.USER_NAME}
                    data["log"] = {}
                    json.dump(data, f)

            with open(log_file, "r") as f:
                data = json.load(f)


            
            t_start = time.time()
            out = func(*args, **kwargs)
            t_end = time.time()
            
            # print (func.__name__)

            data["log"][TIME.get_formatted_current_time()] = {"function_name": func_name_as_record,
                                                                "arguments": args,
                                                                "result": out,
                                                                "script_path": script_path,
                                                                "duration": TIME.get_readable_time(t_end - t_start)
                                                                }

            with open(log_file, "w") as f:
                json.dump(data, f)
  
            return out
        return wrapper
    return decorator





def read_log(user_name = USER.USER_NAME):
    log_file = get_log_file(user_name)
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            data = dict()
            json.dump(data, f)
    with open(log_file, "r") as f:
        data = json.load(f)


    print ("Printing user log from <{}>".format(user_name))
    import pprint
    pprint.pprint(data, indent= 4)




def unit_test():
    pass



    
    
###########################################################
if __name__ == "__main__":
    unit_test()