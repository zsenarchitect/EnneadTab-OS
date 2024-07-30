"""
The main purpose of this module is to add the "public lib" directory to the system path,
allowing us to import Ennead Core modules from that directory.
This import should be added at the top of all extension scripts/modules.

This is only nessary for _revit extension scripts becasue pyRevit has a special lookup
logic that need to follow. Other _app do not need this pather


Why called "proDUCKtion"?
Wrong question, next

Why it is in a "KingDuck.lib" folder? 
No reason. Just a convention. The part matters is the .lib extension
and its location next to the .extension folder.

"""

import os
import sys

# Define the relative path to the "lib" directory (2 levels up, then into "lib")
relative_lib_path = os.path.join('..', '..', 'lib')

# Convert the relative path to an absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.abspath(os.path.join(current_dir, relative_lib_path))

# Add the "lib" directory to sys.path
if lib_dir not in sys.path:
    sys.path.append(lib_dir)







"""
This is to eliminate all the clearup output window step that was needed in the past.
"""
from pyrevit import script #
output = script.get_output()
output.close_others()



def validify():
    """This func do absolutely NOTHING, it is here so when this module is imported
    you can call this func to make it seems like usfule for pylint"""
    pass