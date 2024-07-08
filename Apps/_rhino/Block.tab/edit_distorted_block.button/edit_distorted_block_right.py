__title__ = "EditDistortedBlockRestoreView"
__doc__ = "Go back to previous view stage"


import rhinoscriptsyntax as rs

import edit_block_helper


from EnneadTab import LOG, ERROR_HANDLE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def edit_distorted_block_right():
    rs.EnableRedraw(False)
    edit_block_helper.clear_old_block()

    rs.ShowObjects(rs.HiddenObjects())
    edit_block_helper.restore_camera()
    print ("Resotred")

if __name__ == "__main__":
    edit_distorted_block_right()