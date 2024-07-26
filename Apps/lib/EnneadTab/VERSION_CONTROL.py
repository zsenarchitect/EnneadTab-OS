import os

import EXE
import ENVIRONMENT
import NOTIFICATION

def update_EA_dist():
    EXE.try_open_app("EnneadTab_OS_Installer")



def show_last_success_update_time():
    records = [file for file in os.listdir(ENVIRONMENT.ECO_SYS_FOLDER) if file.endswith(".duck") and not "_ERROR" in file]
    if len(records) == 0:
        NOTIFICATION.messenger("Not successful update recently.\nYour life sucks.")
        return
    records.sort()
    NOTIFICATION.messenger("Most recent update at:\n{}".format(records[-1].replace(".duck", "")))    
        
    pass

def unit_test():
    update_EA_dist()



if __name__ == "__main__":
    # unit_test()
    show_last_success_update_time()