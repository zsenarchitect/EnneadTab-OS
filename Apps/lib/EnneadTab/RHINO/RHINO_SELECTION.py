#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import NOTIFICATION
try:
    import rhinoscriptsyntax as rs
except:
    pass

def is_selection_not_valid(obj, note = "Nothing is selected."):
    if not obj:
        NOTIFICATION.messenger(main_text = note, sub_text = "Action Cancelled")
        return False
    return True

def pay_attention(objs, time = 25, visibility = True, selection = True, zoom_selected = True):
    """zoom flash"""

    original_state = rs.EnableRedraw(True)
    if zoom_selected:
        #rs.UnselectAllObjects()
        rs.SelectObjects(objs)
        rs.ZoomSelected()
        rs.UnselectObjects(objs)


    if objs:
        if visibility:
            for i in range(time):
                rs.FlashObject(objs, style = False)
        if selection:
            for i in range(time):
                rs.FlashObject(objs, style = True)
    rs.EnableRedraw(original_state)
