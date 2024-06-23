
import EXE
import ENVIRONMENT


def update_EA_dist():

    exes = ENVIRONMENT.EXE_FOLDER + "\\EnneadTab_Installer.exe"
    EXE.try_open_app_from_list(exes)
       