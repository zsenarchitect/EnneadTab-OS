
import os
import ENVIRONMENT

def try_open_app(exe_name):
    
    exe = ENVIRONMENT.EXE_FOLDER + "\\{}.exe".format(exe_name)
    if os.path.exists(exe):
        os.startfile(exe)
        return True

        
    if os.environ["USERPROFILE"].split("\\")[-1] == "szhang":
        print ("[SZ only log]No exe found in the location.")
        print (exe)
    return False


