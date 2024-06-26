import shutil
import json
import io
import os
from contextlib import contextmanager


import FOLDER

def _read_json_file_safely(filepath, use_encode=False, create_if_not_exist = False):
    """dup json file then read it to avoid holding the file open status

    Args:
        filepath (_type_): _description_

    Returns:
        dict | None: the content of the json file
    """
    local_path = FOLDER.get_EA_dump_folder_file("temp.json")
    try:
        shutil.copyfile(filepath, local_path)
    except IOError:
        local_path = FOLDER.get_EA_dump_folder_file("temp2.json")
        shutil.copyfile(filepath, local_path)
    # print "###"
    # print local_path
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
    return _read_json_file_safely(filepath, use_encode, create_if_not_exist=create_if_not_exist)



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

    Args:
        dict (_type_): _description_
        file_name (_type_): _description_
        use_encode (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    filepath = FOLDER.get_EA_dump_folder_file(file_name)
    return _save_dict_to_json(dict, filepath, use_encode=use_encode)

def _save_dict_to_json_in_shared_dump_folder(dict, file_name, use_encode=False):
    """direct store dict to a file in shared dump folder

    Args:
        dict (_type_): _description_
        file_name (_type_): _description_
        use_encode (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    filepath = FOLDER.get_shared_dump_folder_file(file_name)
    return _save_dict_to_json(dict, filepath, use_encode=use_encode)

def pretty_print_dict(dict):
    """format print the content of dict or json

    Args:
        dict (_type_): _description_
    """
    string = json.dumps(dict, indent=4)
    print(string)







@contextmanager
def update_data(file_name, is_local = True):
    """
    Usage example
    with DATA_FILE.update_data("abc.json") as data:
        data['new_key'] = 'new_value'  # Update data here
    """

        
    try:
        if is_local:
            data = _read_json_as_dict_in_dump_folder(file_name, use_encode=True, create_if_not_exist=True)
        else:
            data = _read_json_as_dict_in_shared_dump_folder(file_name, use_encode=True, create_if_not_exist=True)

        # temporarily hands control back to the caller, allowing them to modify data.
        yield data
        # Once the block inside the with statement is complete, 
        # control returns to the context manager, which writes the modified data back to the file.


        if is_local:
            _save_dict_to_json_in_dump_folder(data, file_name, use_encode=True)
        else:
            _save_dict_to_json_in_shared_dump_folder(data, file_name, use_encode=True)

    except Exception as e:
        print("An error occurred when updating data: {}".format(e))
