import FOLDER
import DATA_FILE

def _get_setting_file():
    """this is the ui setting file for EnneadTab stored in each user local computer

    Returns:
        _type_: _description_
    """
    file_name = 'global_setting.json'
    return FOLDER.get_EA_dump_folder_file(file_name)


def get_setting_data(key, defaule_value=None):
    """if no key provided, will return the whole dict
        otherwise, return the value of this key, default value 

        key_defaule_value: (key, default value), a tuple of default result, this is used to get the key of value looking for. If do not provide this tuple, then return the raw while data"""
    setting_file = _get_setting_file()
    data = DATA_FILE.get_data(setting_file)
    return data.get(key, defaule_value)


def set_setting_data(key, value):
    """set the key and value to the revit ui setting

    Args:
        key (_type_): _description_
        value (_type_): _description_
    """
    setting_file = _get_setting_file()
    with DATA_FILE.update_data(setting_file) as data:
        data[key] = value




# simply rename the addin file register file by 
# add/remove .disabled at end of the .addin file
# note need to search for all valid version folder
def enable_revit_addin(addin):
    pass

    # reload pyrevit

def disable_revit_addin(addin):
    pass

    # reload pyrevit
    