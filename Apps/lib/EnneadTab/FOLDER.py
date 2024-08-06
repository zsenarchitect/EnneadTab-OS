import time
import os
import shutil
import ENVIRONMENT

def copy_file(original_path, new_path):
    target_folder = os.path.dirname(new_path)
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)
    shutil.copyfile(original_path, new_path)

    
def copy_file_to_folder(original_path, target_folder):
    new_path = original_path.replace(os.path.dirname(original_path), target_folder)
    try:
        shutil.copyfile(original_path, new_path)
    except Exception as e:
        print (e)

    return new_path

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






def get_EA_dump_folder_file(file_name):
    """include extension"""
    return "{}\\{}".format(ENVIRONMENT.DUMP_FOLDER, file_name)


def get_shared_dump_folder_file(file_name):
    """include extension"""
    return "{}\\{}".format(ENVIRONMENT.SHARED_DUMP_FOLDER, file_name)




def copy_file_to_local_dump_folder(original_path, file_name = None, ignore_warning=False):
    if file_name is None:
        file_name = original_path.rsplit("\\", 1)[1]

    local_path = get_EA_dump_folder_file(file_name)
    try:
        shutil.copyfile(original_path, local_path)
    except Exception as e:
        if not ignore_warning:
            if "being used by another process" in str(e):
                print("Please close opened file first.")
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



def cleanup_folder_by_extension(folder = "folder path",
                                extension = "extension"):
    """remove files in folder based on extension"""
    filenames = os.listdir(folder)

    count = 0
    for current_file in filenames:
        ext = os.path.splitext(current_file)[1]
        if ext.upper() == extension.upper():
            try:
                os.remove(os.path.join(folder, current_file))
                count += 1
            except Exception as e:
                print ("Cannot delete file [{}] becasue error: {}".format(current_file, e))
    return count



def secure_filename_in_folder(output_folder, desired_name, extension):
    """make sure the desired name of file is formated as such in the output folder.
    This is usually a requirement after export revit jpg becasue revit will auto append other name in the jpg export.

    Args:
        output_folder (str): folder to search
        desired_name (str): desired final name, also the name to search for among existing files in output folder. THIS NAME DOES NOT CONTAIN EXTENSION.
        extension (str): extension to lock search. THIS CONTAINS DOT, such as ".xxx"
    """
    
    
    try:
        os.remove(os.path.join(output_folder, desired_name + extension))
    except:
        pass

    #print keyword
    keyword = " - Sheet - "

    for file_name in os.listdir(output_folder):
        if desired_name in file_name and extension in file_name.lower():
            new_name = desired_name


            # this prefix allow longer path limit
            old_path = "\\\\?\\{}\\{}".format(output_folder, file_name)
            new_path = "\\\\?\\{}\\{}".format(output_folder, new_name + extension)
            try:
                os.rename(old_path, new_path)

            except:
                try:
                    
                    os.rename(os.path.join(output_folder, file_name),os.path.join(output_folder, new_name + extension))

                except Exception as e:
                    ERROR_HANDLE.print_note( "filename clean up failed: skip {} becasue: {}".format(file_name, e))
