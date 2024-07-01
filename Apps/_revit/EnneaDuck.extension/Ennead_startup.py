

import os
import sys

"""need to navigate to duckking lib first before it can auto detect further. This is special treatment for te startup script only"""
# Define the relative path to the "lib" directory (2 levels up, then into "lib")
relative_lib_path = os.path.join('..',  'KingDuck.lib')

# Convert the relative path to an absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.abspath(os.path.join(current_dir, relative_lib_path))

# Add the "lib" directory to sys.path
if lib_dir not in sys.path:
    sys.path.append(lib_dir)





import proDUCKtion # pyright: ignore 

from EnneadTab import VERSION_CONTROL



def main():
    VERSION_CONTROL.update_EA_dist()



if __name__ == "__main__":
    main()