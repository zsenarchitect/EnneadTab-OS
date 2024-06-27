
import os
import shutil
import NOTIFICATION

def secure_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)
    return folder

def get_user_folder():
    return "{}\Documents".format(os.environ["USERPROFILE"])

def get_appdata_folder():
    return "{}\AppData".format(os.environ["USERPROFILE"])


def get_desktop_folder():
    return os.path.expandvars('%userprofile%\\desktop')

def get_download_folder():
    return os.path.expandvars('%userprofile%\\downloads')

def get_EA_local_dump_folder():
    return secure_folder(get_user_folder() + "\\EnneadTab Ecosystem\\Dump") 


def get_EA_dump_folder_file(file_name):
    """include extension"""
    return "{}\\{}".format(get_EA_local_dump_folder(), file_name)


def get_shared_dump_folder_file(file_name):
    """include extension"""
    return "{}\\{}".format(ENVIRONMENT.SHARED_DATA_DUMP_FOLDER, file_name)




def copy_file_to_local_dump_folder(original_path, file_name = None, ignore_warning=False):
    if file_name is None:
        file_name = original_path.rsplit("\\", 1)[1]

    local_path = get_EA_dump_folder_file(file_name)
    try:
        shutil.copyfile(original_path, local_path)
    except Exception as e:
        if not ignore_warning:
            if "being used by another process" in str(e):
                NOTIFICATION.messenger("Please close opened file first.")
            else:
                raise e

    return local_path
