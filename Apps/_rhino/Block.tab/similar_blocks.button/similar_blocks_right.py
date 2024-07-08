
__title__ = "IsolateSimilarBlocks"
__doc__ = "Isolate blocks of similar definitions from the selected blocks"
import rhinoscriptsyntax as rs

from EnneadTab import NOTIFICATION, LOG, ERROR_HANDLE

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def similar_blocks():


    orginal_blocks = rs.GetObjects("Select block instances to isolate", filter = 4096, preselect = True)
    if orginal_blocks is None:
        NOTIFICATION.messenger("No block instances selected.")
        return
    rs.EnableRedraw(False)
    
    block_names = [rs.BlockInstanceName(x) for x in orginal_blocks]
    block_names = list(set(block_names))
    
    block_collection = []
    for block_name in block_names:
        block_collection.extend(rs.BlockInstances(block_name))

    rs.UnselectAllObjects()
    rs.SelectObjects( block_collection)
    invert_objs = rs.InvertSelectedObjects(include_lights = True, include_grips = True, include_references = True)
    rs.HideObjects(invert_objs)


if __name__ == "__main__":
    similar_blocks()
