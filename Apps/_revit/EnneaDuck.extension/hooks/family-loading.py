
"""
store session script data to a temp file
https://pyrevit.readthedocs.io/en/latest/pyrevit/coreutils/appdata.html


share parameter between script
https://pyrevit.readthedocs.io/en/latest/pyrevit/coreutils/envvars.html
"""


from pyrevit import script
from pyrevit import EXEC_PARAMS
# from pyrevit.coreutils import appdata
from pyrevit.coreutils import envvars
import time
import pickle
envvars.set_pyrevit_env_var("FAMILY_LOAD_BEGIN", time.time())
datafile = script.get_instance_data_file("sub_c_list")

# print datafile


def get_subc(category):
    temp = []
    for c in category:
        for sub_c in c.SubCategories:
            temp.append("[{0}]--->[{1}]".format(c.Name, sub_c.Name))
    return temp

############### main ###################
if __name__ == "__main__":

    doc = EXEC_PARAMS.event_args.Document

    all_Cs = doc.Settings.Categories

    data = get_subc(all_Cs)

    f = open(datafile, 'w')
    pickle.dump(data, f)
    f.close()
