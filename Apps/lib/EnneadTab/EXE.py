
import os


def try_open_app_from_list(exes):
    for exe in exes:
        if not exe:
            continue
        if os.path.exists(exe):
            os.startfile(exe)
            return True
    if os.environ["USERPROFILE"].split("\\")[-1] == "szhang":
        print ("[SZ only log]No exe found in any of the location.")
        for exe in exes:
            print (exe)
    return False

