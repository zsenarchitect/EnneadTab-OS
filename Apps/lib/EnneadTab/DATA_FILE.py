import time
import shutil
import json
import io
import os
import traceback
from contextlib import contextmanager


import FOLDER

def _read_json_file_safely(filepath, use_encode=False, create_if_not_exist = False):
    """dup json file then read it to avoid holding the file open status

    Args:
        filepath (_type_): _description_

    Returns:
        dict | None: the content of the json file
    """
    local_path = FOLDER.get_EA_dump_folder_file("temp.sexyDuck")
    try:
        shutil.copyfile(filepath, local_path)
    except IOError:
        local_path = FOLDER.get_EA_dump_folder_file("temp_additional.sexyDuck")
        shutil.copyfile(filepath, local_path)

    content = _read_json_as_dict(local_path, use_encode, create_if_not_exist)
    return content


def _read_json_as_dict(filepath, use_encode=False, create_if_not_exist = False):
    """get the data saved in json as dict

    Args:
        filepath (_type_): _description_
        use_encode (bool, optional): for Chinese char file it might need encoding. Defaults to False.

    Returns:
        dict | None: _description_
    """
    if create_if_not_exist:
        if not os.path.exists (filepath):
            _save_dict_to_json({},filepath, use_encode)
            return dict()


    try:
        if use_encode:
            with io.open(filepath, encoding='utf8') as f:
                data = json.load(f)
            return data

        else:
            with open(filepath, "r") as f:
                data = json.load(f)
            return data
    except Exception as e:
        print(e)
        return None


def _read_json_as_dict_in_dump_folder(file_name, use_encode=False, create_if_not_exist=False):
    """direct access the json file from dump folder

    Args:
        file_name (_type_): _description_
        use_encode (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    filepath = FOLDER.get_EA_dump_folder_file(file_name)
    return _read_json_as_dict(filepath, use_encode, create_if_not_exist)

def _read_json_as_dict_in_shared_dump_folder(file_name, use_encode=False, create_if_not_exist=False):
    """direct access the json file from shared dump folder

    Args:
        file_name (_type_): _description_
        use_encode (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    filepath = FOLDER.get_shared_dump_folder_file(file_name)
    return _read_json_file_safely(filepath, use_encode, create_if_not_exist)



def _save_dict_to_json(dict, filepath, use_encode=False):
    """store the python dict to json at path

    Args:
        dict (_type_): _description_
        filepath (_type_): _description_
        use_encode (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    try:
        if use_encode:
            with io.open(filepath, 'w', encoding='utf-8') as f:
                # Serialize the data and write it to the file
                json.dump(dict, f, ensure_ascii=False, indent=4)
            return True

        else:
            with open(filepath, "w") as f:
                json.dump(dict, f, indent=4)
             
            return True
    except Exception as e:
        print(e)
        return False



    

def _save_dict_to_json_in_dump_folder(dict, file_name, use_encode=False):
    """direct store dict to a file in dump folder
    """
    filepath = FOLDER.get_EA_dump_folder_file(file_name)
    return _save_dict_to_json(dict, filepath, use_encode=use_encode)

def _save_dict_to_json_in_shared_dump_folder(dict, file_name, use_encode=False):
    """direct store dict to a file in shared dump folder
    """
    filepath = FOLDER.get_shared_dump_folder_file(file_name)
    return _save_dict_to_json(dict, filepath, use_encode=use_encode)




def get_list(filepath="path"):
    extention = FOLDER.get_file_extension_from_path(filepath)
    local_path = FOLDER.get_EA_dump_folder_file("temp{}".format(extention))
    shutil.copyfile(filepath, local_path)


    with io.open(local_path, encoding="utf8") as f:
        lines = f.readlines()
  
    return map(lambda x: x.replace("\n", ""), lines)


def set_list(list, filepath, end_with_new_line=False):

    with io.open(filepath, "w", encoding="utf8") as f:
        f.write('\n'.join(list))
        if end_with_new_line:
            f.write("\n")

    return True

#######################################################################################



def pretty_print_dict(dict):
    """format print the content of dict or json
    """
    string = json.dumps(dict, indent=4)
    print(string)





def get_data(file_name, is_local = True):
    
    if is_local:
        return _read_json_as_dict_in_dump_folder(file_name, use_encode=True, create_if_not_exist=True)
    else:
        return _read_json_as_dict_in_shared_dump_folder(file_name, use_encode=True, create_if_not_exist=True)

def set_data(data, file_name, is_local = True):
    
    if is_local:
        _save_dict_to_json_in_dump_folder(data, file_name, use_encode=True)
    else:
        _save_dict_to_json_in_shared_dump_folder(data, file_name, use_encode=True)

@contextmanager
def update_data(file_name, is_local = True):
    """
    prefer just the file_name, but full path is ok
    
    Usage example
    with DATA_FILE.update_data("abc.sexyDuck") as data:
        data['new_key'] = 'new_value'  # Update data here
    """

    if os.path.exists(file_name):
        file_name = os.path.basename(file_name)

        
    try:
        data = get_data(file_name, is_local)

        # temporarily hands control back to the caller, allowing them to modify data.
        yield data
        # Once the block inside the with statement is complete, 
        # control returns to the context manager, which writes the modified data back to the file.

        set_data(data, file_name, is_local)

    except Exception:
        print("An error occurred when updating data:\n{}".format(traceback.format_exc()))





#######################################


STCIKY_FILE = "sticky.SexyDuck"

def get_sticky(sticky_name, default_value_if_no_sticky=None):
    """get longterm sticky information

    Args:
        sticky_name (str): name of the sticky
        default_value_if_no_sticky (_type_, optional): _description_. Defaults to None.

    Returns:
        any : get the value of the longterm sticky
    """
   
    data = get_data(STCIKY_FILE)
    if sticky_name not in data.keys():
        set_sticky(sticky_name, default_value_if_no_sticky)
        return default_value_if_no_sticky
    return data[sticky_name]


def set_sticky(sticky_name, value_to_write):
    """set a long term sticky. The long term sticky will not be cleared after the application is closed.

    Args:
        sticky_name (str): _description_
        value_to_write (any): value to write
    """
    with update_data(STCIKY_FILE) as data:
        data[sticky_name] = value_to_write




