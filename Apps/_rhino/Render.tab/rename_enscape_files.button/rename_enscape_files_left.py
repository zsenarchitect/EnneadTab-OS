
__title__ = "RenameEnscapeFiles"
__doc__ = "Rename the output of Enscape files to remove the long bit."

import os
import rhinoscriptsyntax as rs

def rename_enscape_files():
    file_names = rs.OpenFileNames()
    for file_name in file_names:
        print (file_name)

        head, tail = os.path.split(file_name)
        try:
            new_tail = tail.split("_", 2)[2]# max split is 2, then use index 2 of the output
        except Exception as e:
            print (e)
            continue
        src = file_name
        dst = "{}\{}".format(head, new_tail)
        try:
            os.rename(src, dst)
        except Exception as e:
            print( e)
            rs.MessageBox("This file rename <{}> is skipped, check for if same file name already exist.".format(new_tail))