import FOLDER
import DATA_FILE
import USER


SETTING_FILE_NAME = 'setting_{}.sexyDuck'.format(USER.USER_NAME)

def get_setting(key, defaule_value=None):
    """if no key provided, will return the whole dict
        otherwise, return the value of this key, default value 

        key_defaule_value: (key, default value), a tuple of default result, this is used to get the key of value looking for. If do not provide this tuple, then return the raw while data"""

    data = DATA_FILE.get_data(SETTING_FILE_NAME)
    return data.get(key, defaule_value)


def set_setting(key, value):
    """set the key and value to the revit ui setting

    Args:
        key (_type_): _description_
        value (_type_): _description_
    """

    with DATA_FILE.update_data(SETTING_FILE_NAME) as data:
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


