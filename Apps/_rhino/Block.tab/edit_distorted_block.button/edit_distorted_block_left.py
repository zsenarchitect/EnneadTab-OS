__title__ = "EditDistortedBlock"
__doc__ = "Edit distorted block by editing a copy."



import rhinoscriptsyntax as rs
from EnneadTab import NOTIFICATION



import edit_block_helper



def edit_distorted_block_left():


    edit_block_helper.clear_old_block()

        
    obj = rs.GetObject("Pick block to edit.", filter=rs.filter.instance)
    if not obj:
        NOTIFICATION.messenger("No block selected...")
        return
    rs.EnableRedraw(False)
    edit_block_helper.save_camera()
    edit_block_helper.remember_selection(obj)
    
    block_name = rs.BlockInstanceName(obj)

    temp_block = rs.InsertBlock(block_name, [0,0,0])
    rs.ObjectName(temp_block, edit_block_helper.TEMP_BLOCK_NAME)
    rs.UnselectAllObjects()
    rs.SelectObject(temp_block)
    rs.ZoomSelected()

    cam, target = rs.ViewCameraTarget()
    if target[1]-cam[1] < 0:
        new_cam = [cam[0], -cam[1], cam[2]]
        rs.ViewCameraTarget(None, new_cam, target)
    
    rs.InvertSelectedObjects()
    rs.HideObjects(rs.SelectedObjects())
    rs.UnselectAllObjects()

    NOTIFICATION.messenger("After commit, right click to restore previous camera")

