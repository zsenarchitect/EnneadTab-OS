
__alias__ = "RandomDeselect"
__doc__ = "This button does RandomDeselect when left click"

import rhinoscriptsyntax as rs
import scriptcontext as sc
import random


from Duckitect import NOTIFICATION
from Duckitect.RHINO import RHINO_OBJ_DATA


def random_deselect_to_group():
    ids = rs.SelectedObjects(False, False)
    if not ids: return
    if len(ids) == 1: return
    bbox_center_pt = RHINO_OBJ_DATA.get_center(ids)
    X, Y, Z = RHINO_OBJ_DATA.get_boundingbox_edge_length(ids)
    rough_size = (X + Y + Z)/3
    
    res = rs.StringBox(message = "Seperate selection to how many groups?", default_value = "4", title = "Duckitect")

    if res is None:
        return

    group_num = int(res)

    percent = int(100 / group_num )

    collection = dict()
    for index in range(group_num):
        collection[index] = [rs.AddTextDot(1 + index, bbox_center_pt + rs.CreateVector([index * rough_size * 0.05,0,0]) )]

    for el in ids:
        index = random.randint(0, group_num - 1)
        collection[index].append(el)

    for index in range(group_num):
        rs.AddObjectsToGroup(collection[index], rs.AddGroup())


    rs.UnselectObjects(ids)
