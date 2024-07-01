__alias__ = "EditDistortedBlockRestoreView"
__doc__ = "Go back to previous view stage"


import rhinoscriptsyntax as rs

import edit_block_helper



def edit_distorted_block_right():
    rs.EnableRedraw(False)
    edit_block_helper.clear_old_block()

    rs.ShowObjects(rs.HiddenObjects())
    edit_block_helper.restore_camera()
    print ("Resotred")

