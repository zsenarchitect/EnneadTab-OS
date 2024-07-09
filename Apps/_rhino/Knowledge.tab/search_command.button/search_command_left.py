__title__ = "SearchCommand"
__doc__ = "Learn all the buttons functions."


import os

from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_ALIAS

# this is for the interactive search UI that gives the detail explanation of evrything
def get_all_data():
    

                
    return data         



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def search_command():
    RHINO_ALIAS.register_alias_set()
    print ("Placeholder func <{}> that does this:{}".format(__title__, __doc__))




if __name__ == "__main__":
    search_command()