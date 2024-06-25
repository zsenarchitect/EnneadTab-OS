
import os

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