import shutil
import os
import time
import ENVIRONMENT
import USER
import NOTIFICATION

def try_open_app(exe_name, legacy_name = None, safe_open = False):
    """extension optional
    legacy_name if for legacy support just in case, 
    but alwasys should put preferred exe_name as first arg

    if use safe open, it will make a temp copy of the exe in dump folder and run that
    there are purged as it go. This is to address the issue that cannot update exe when it is being used.
    Do not accept foldered exe as this will make it harder to make temp folder? maybe later find a way but now keep it simple.
    """

    abs_name = exe_name.lower()
    if abs_name.endswith(".3dm") or abs_name.endswith(".xlsx") or abs_name.endswith(".xls") or abs_name.endswith(".pdf") or abs_name.endswith(".png") or abs_name.endswith(".jpg"):
        os.startfile(exe_name)
        return True
    


    exe_name = exe_name.replace(".exe", "")
    exe = ENVIRONMENT.EXE_PRODUCT_FOLDER + "\\{}.exe".format(exe_name)

    if safe_open:
        if not os.path.exists(exe):
            raise Exception("Only work for stanfle along exe, not for foldered exe.")
        temp_exe_name = "_temp_exe_{}_{}.exe".format(exe_name, int(time.time()))
        temp_exe = ENVIRONMENT.DUMP_FOLDER + "\\" + temp_exe_name
        # print (temp_exe)
        shutil.copyfile(exe, temp_exe)
        os.startfile(temp_exe)
        for file in os.listdir(ENVIRONMENT.DUMP_FOLDER):
            if file.startswith("_temp_exe_"):
                try:
                    os.remove(os.path.join(ENVIRONMENT.DUMP_FOLDER, file))
                except:
                    pass
        return True
        
    
        
    if os.path.exists(exe):
        os.startfile(exe)
        return True
    foldered_exe = ENVIRONMENT.EXE_PRODUCT_FOLDER + "\\{0}\\{0}.exe".format(exe_name)
    if os.path.exists(foldered_exe):
        os.startfile(foldered_exe)
        return True
    
    if legacy_name:
        if try_open_app(legacy_name):
            return True
        
    if USER.IS_DEVELOPER:
        print ("[Developer only log]No exe found in the location.")
        print (exe)
        print (foldered_exe)
        NOTIFICATION.messenger("No exe found!!!\n{}".format(exe_name))
    return False


