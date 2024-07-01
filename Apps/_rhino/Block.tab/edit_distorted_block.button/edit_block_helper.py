
import rhinoscriptsyntax as rs
import scriptcontext as sc


TEMP_BLOCK_NAME = "EA_TEMP_EDIT_BLOCK"
TEMP_BLOCK_VIEW_DATA = "EA_TEMP_EDIT_BLOCK_VIEW_DATA"
TEMP_BLOCK_SOURCE_ID = "EA_TEMP_EDIT_BLOCK_SOURCE_ID"




def clear_old_block():
    old_blocks = rs.ObjectsByName(TEMP_BLOCK_NAME)
    if old_blocks:
        rs.DeleteObjects(old_blocks)

def remember_selection(obj):
    sc.sticky[TEMP_BLOCK_SOURCE_ID] = obj
    

def save_camera():
    camera, target = rs.ViewCamera(), rs.ViewTarget()
    print ("save camera camera and target")
    print (camera)
    print (target)
    sc.sticky[TEMP_BLOCK_VIEW_DATA] = camera, target


def restore_camera():
    if TEMP_BLOCK_VIEW_DATA not in sc.sticky:
        return
    camera, target = sc.sticky[TEMP_BLOCK_VIEW_DATA]
    print ("restore camera camera and target")
    print (camera)
    print (target)
    rs.ViewCameraTarget(None, camera, target)
    # rs.ViewCamera(None,camera)
    # rs.ViewTarget(None,target)
    # if target[1]-camera[1] < 0:
    #     new_cam = [camera[0], -camera[1], camera[2]]
    #     rs.ViewCameraTarget(None, new_cam, target)

    del sc.sticky[TEMP_BLOCK_VIEW_DATA]

    return


    if TEMP_BLOCK_SOURCE_ID in sc.sticky:
        obj = sc.sticky[TEMP_BLOCK_SOURCE_ID]
        if rs.IsObject(obj):
            rs.UnselectAllObjects()
            rs.SelectObject(obj)
            rs.ZoomSelected()
            rs.UnselectObject(obj)
            
            del sc.sticky[TEMP_BLOCK_SOURCE_ID]


            


