
import os
import ENVIRONMENT
import USER
import NOTIFICATION

def try_open_app(exe_name, legacy_name = None):
    """extension optional
    legacy_name if for legacy support just in case, but alwasys should put preferred exe_name as first arg"""
    if not exe_name.endswith(".exe"):
        # this is might not be a exe from EnneadTab, such as excel file
        os.startfile(exe_name)
        return True

    exe_name = exe_name.replace(".exe", "")
    exe = ENVIRONMENT.EXE_PRODUCT_FOLDER + "\\{}.exe".format(exe_name)
        
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


