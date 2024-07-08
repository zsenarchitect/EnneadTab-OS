__title__ = "SectionboxByPolysrf"
__doc__ = "Use closed polysrf as input box cutter."


import os
import rhinoscriptsyntax as rs

from EnneadTab import NOTIFICATION, SOUND
from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_CLEANUP

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)) + "\\section_box_cleanup.button")
import section_box_cleanup_left as SBC


import section_box_utility


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def section_box(group_name_key_word=section_box_utility.GROUP_NAME_KEYWORD, clean_up_only=False, predefined_polysurf=None):



    #group_name_key_word = "EnneadTab_SectionBox_"
    SBC.section_box_cleanup(group_name_key_word)
    if clean_up_only:
        return


    # group names contains view name, so each view can have seperate clipping
    # remove clippplane group by name
    clip_group_name = group_name_key_word + "clip planes_" + rs.CurrentView()
    edge_group_name = group_name_key_word + "edges_" + rs.CurrentView()





    # get user polysurf
    if predefined_polysurf:
        input_polysurf = predefined_polysurf

    else:
        input_polysurf = rs.GetObject(message = "pick closed polysurface as sectionbox",filter = rs.filter.polysurface,  preselect = True)
    print (input_polysurf)
    rs.UnselectAllObjects()
    if input_polysurf is None:
        NOTIFICATION.toast(main_text = "you didn't selection a predefined polysurface")
        return

    # create clip plane for each face
    clip_planes = []

    for i, surf in enumerate (rs.ExplodePolysurfaces(input_polysurf, delete_input = False)):
        if not rs.IsSurfacePlanar(surf):
            rs.MessageBox("you have non-planar surface in the polysurf.")
            return
        rs.SelectObject(surf)
        rs.Command("_flip  -enter")
        rs.UnselectObject(surf)
        #rs.FlipSurface(surf, flip = True)
        frame = rs.SurfaceFrame(surf, [0.0,0.0])
        clip_plane = rs.AddClippingPlane(frame, 1000, 1000, views = None)
        rs.DeleteObject(surf)
        clip_planes.append(clip_plane)
        rs.ObjectName(clip_plane, name = group_name_key_word + "clip plane" + str(i))


    #group clip planes
    clip_group_name = RHINO_CLEANUP.get_good_name(clip_group_name, rs.GroupNames())
    edge_group_name = RHINO_CLEANUP.get_good_name(edge_group_name, rs.GroupNames())
    rs.AddGroup(group_name = clip_group_name)
    rs.AddObjectsToGroup(clip_planes, clip_group_name)



    # dup edges of input polysurf, group and ?make dash?
    edges = rs.DuplicateEdgeCurves(input_polysurf)
    try:
        rs.ObjectLinetype(edges, linetype = "Hidden")
        rs.Command("_setlinetypescale 100 -enter")
        rs.ObjectName(edges, name = group_name_key_word + "edges" )
    except Exception as e:
        print (e)
    rs.AddGroup(group_name = edge_group_name)
    rs.AddObjectsToGroup(edges, edge_group_name)

    #hide input polysrf if it is customized poly surf, otherwise just delete the bbobx
    if predefined_polysurf:
        rs.DeleteObject(input_polysurf)
    else:
        rs.HideObject(input_polysurf)
    #hide clip planes
    rs.HideGroup(clip_group_name)

    play_sound()



def play_sound():

    file = "sound effect_popup msg3.wav"
    SOUND.play_sound(file)



#######################################

if __name__ == "__main__":
    rs.EnableRedraw(False)
    section_box(GROUP_NAME_KEYWORD)
