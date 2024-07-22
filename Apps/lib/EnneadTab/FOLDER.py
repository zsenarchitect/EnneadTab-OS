import time
import os
import shutil
import NOTIFICATION

def secure_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)
    return folder



def get_user_folder():
    return "{}\\Documents".format(os.environ["USERPROFILE"])



def get_file_name_from_path(file_path, include_extension=True):

    head, tail = os.path.split(file_path)
    if not include_extension:
        tail = tail.split(".")[0]
    return tail

def get_file_extension_from_path(file_path):
    return os.path.splitext(file_path)[1]



def get_appdata_folder():
    return "{}\\AppData".format(os.environ["USERPROFILE"])


def get_desktop_folder():
    return os.path.expandvars('%userprofile%\\desktop')

def get_download_folder():
    return os.path.expandvars('%userprofile%\\downloads')

def get_EA_local_dump_folder():
    return get_user_folder() + "\\EnneadTab Ecosystem\\Dump"


def get_EA_dump_folder_file(file_name):
    """include extension"""
    return "{}\\{}".format(get_EA_local_dump_folder(), file_name)


def get_shared_dump_folder_file(file_name):
    """include extension"""
    DB_FOLDER = "L:\\4b_Applied Computing\\EnneadTab-DB"
    SHAERD_DUMP_FOLDER = DB_FOLDER + "\\Shared Data Dump"
    return "{}\\{}".format(SHAERD_DUMP_FOLDER, file_name)




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



def backup_data(data_file_name, backup_folder_title, max_time = 60*60*24*1):
    def decorator(func):
        def wrapper(*args, **kwargs):

            out = func(*args, **kwargs)

            
            backup_folder = get_EA_dump_folder_file("backup_" + backup_folder_title)
            if not os.path.exists(backup_folder):
                os.mkdir(backup_folder)
                
            latest_backup_date = None
            for filename in os.listdir(backup_folder):
                if not filename.endswith(".sexyDuck"):
                    continue
                backup_date_str = filename.split("_")[0]
                backup_date = time.strptime(backup_date_str, "%Y-%m-%d")
                if not latest_backup_date or backup_date > latest_backup_date:
                    latest_backup_date = backup_date

            today = time.strftime("%Y-%m-%d")
            if not latest_backup_date or (time.mktime(time.strptime(today, "%Y-%m-%d")) - time.mktime(latest_backup_date)) > max_time:
                backup_file_path = os.path.join(backup_folder, "{}_{}".format(today, data_file_name))
            
                if os.path.exists(get_EA_dump_folder_file(data_file_name)):
                    shutil.copy(get_EA_dump_folder_file(data_file_name), backup_file_path)
  
            return out
        return wrapper
    return decorator
