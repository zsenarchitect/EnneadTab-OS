
__title__ = "SectionBoxCleanup"
__doc__ = "Reset the view to unbounded."


import os
import rhinoscriptsyntax as rs

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)) + "\\section_box.button")
import section_box_utility

def section_box_cleanup(group_name_key_word=section_box_utility.GROUP_NAME_KEYWORD):
    if rs.GroupNames() is None:
        return
    for group_name in  rs.GroupNames():
        if group_name_key_word in group_name:
            print ("group [{}] will be deleted.".format(group_name))
            rs.ShowGroup(group_name)
            group_objs = rs.ObjectsByGroup(group_name)
            print (group_objs)
            rs.DeleteObjects(group_objs)
            
            rs.DeleteGroup(group_name)
            
    
    for obj in rs.AllObjects():
        if not rs.ObjectName(obj):
            continue
        if group_name_key_word in rs.ObjectName(obj):
            print ("going to delete obj")
            rs.DeleteObject(obj)
    
    #rs.Redraw()
    
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_Yes _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")