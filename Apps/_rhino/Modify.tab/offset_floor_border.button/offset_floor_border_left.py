
__title__ = "OffsetFloorBorder"
__doc__ = "Shrink/Expand the border of floor for input srf or polysrfs. The thickness is retained if using polysrf."


import random
import traceback


import rhinoscriptsyntax as rs
import scriptcontext as sc
from EnneadTab.RHINO import RHINO_OBJ_DATA, RHINO_FORMS, RHINO_SELECTION
from EnneadTab import NOTIFICATION, DATA_FILE, COLOR




def is_facing_up(face):
    param = rs.SurfaceClosestPoint(face, RHINO_OBJ_DATA.get_center(face))
    normal = rs.SurfaceNormal(face, param)
    #print normal
    Z_up = [0,0,1]
    t = 0.01
    if -t < rs.VectorAngle(normal, Z_up) < t:
        return True
    return False

def total_prim_length(obj):
    edges = rs.DuplicateEdgeCurves(obj)
    total = sum([rs.CurveLength(x) for x in edges])
    rs.DeleteObjects(edges)
    return total

def process_polysurf(poly_surf, offset):
    h = RHINO_OBJ_DATA.get_obj_h(poly_surf)
    backup = rs.CopyObject(poly_surf)
    all_faces = rs.ExplodePolysurfaces(poly_surf, delete_input = True)


    faces = filter(is_facing_up, all_faces)
    if not faces:
        RHINO_FORMS.notification(main_text = "Cannot get a valid up-facing surface, your geometry might have some issue. Skip.",
                                    sub_text = "I am going to flash it for you so you know which I am talking about..",
                                    height = 300)
        RHINO_SELECTION.pay_attention(all_faces)
        rs.DeleteObjects(all_faces)
        COLOR.invert_color(backup)

        return backup

    face = faces[0]
    # trash_faces = filter(lambda x: x != face, all_faces)


    new_face = process_surf(face, offset)
    if new_face == face:
        rs.DeleteObjects(all_faces)
        COLOR.invert_color(backup)

        return backup



    path = rs.AddLine([0,0,0], [0,0,-h])
    new_brep = rs.ExtrudeSurface(new_face, path, cap = True)
    trash = [path, new_face, backup]
    rs.DeleteObjects(trash)
    for trash in all_faces:
        if trash:
            rs.DeleteObject(trash)

    return new_brep


def get_point_on_srf(srf):
    test_pt = RHINO_OBJ_DATA.get_center(srf)
    # any_
    domainU = rs.SurfaceDomain(srf, 0)
    domainV = rs.SurfaceDomain(srf, 1)
    max_count = 100
    count = 0
    while not rs.IsPointOnSurface(srf,test_pt):
        u = (domainU[1] - domainU[0]) * random.random()
        v = (domainV[1] - domainV[0]) * random.random()
        test_pt = rs.EvaluateSurface(srf, u, v)
        count += 1
        
        if count > max_count:
            break
    return test_pt

    

def process_surf(srf, offset):
    border = rs.DuplicateSurfaceBorder(srf, type = 1) #externior only

    if not border:
        rs.Command("!_DuplicateBorder -Enter ")
        border = rs.LastCreatedObjects()


    if not border:
        rs.AddTextDot("Cannot get a valid border from your geometry\nPlease process this guy manually.", RHINO_OBJ_DATA.get_center(srf))

        # RHINO_FORMS.notification(main_text = "Cannot get a valid border, your geometry might have some issue.. Skip.",
        #                             sub_text = "I am going to flash it for you so you know which I am talking about..",
        #                             height = 300)
        RHINO_SELECTION.pay_attention(srf)
        COLOR.invert_color(srf)
        return srf

    found = False
    for res in border:
        if found:
            try:
                rs.DeleteObject(res)
            except:
                pass
        try:
            # print (res)
            if rs.SimplifyCurve(res):
                border = res
                found = True
        except:
            pass



    direction = RHINO_OBJ_DATA.get_center(srf)
    direction = get_point_on_srf(srf)

    if not rs.IsPointOnSurface(srf, direction):
        rs.AddTextDot("Center of the face is outside the boundary. Skip.", RHINO_OBJ_DATA.get_center(srf))
        # RHINO_FORMS.notification(main_text = "Center of the face is outside the boundary. Skip.",
        #                             sub_text = "I am going to flash it for you so you know which I am talking about..",
        #                             height = 300)

        rs.DeleteObjects([border])
        RHINO_SELECTION.pay_attention(srf)
        COLOR.invert_color(srf)

        return srf

    new_border = rs.OffsetCurve(border, direction, offset)

    if not new_border:
        rs.AddTextDot("This surface cannot get a valid offset from the boundary.\nPlease process this guy manually.", RHINO_OBJ_DATA.get_center(srf))
        # RHINO_FORMS.notification(main_text = "Cannot get a valid offset from the boundary, your geometry might have some issue. Skip.",
        #                             sub_text = "I am going to flash it for you so you know which I am talking about..",
        #                             height = 300)

        rs.DeleteObjects([border])
        RHINO_SELECTION.pay_attention(srf)
        COLOR.invert_color(srf)

        return srf

    # print new_border
    found = False
    for res in new_border:
        if rs.IsCurveClosed(res):
            new_border = res
            found = True
            break
    if not found:
        rs.Command("!_Offset _Distance {} -Enter -Enter ".format(offset))
        new_border = rs.LastCreatedObjects()
        if isinstance(new_border, list):
            new_border = new_border[0]
        if not new_border:
            new_border = rs.FirstObject()
        print ("Using rs command method: " + str(new_border    ))
    
    try:
        if not rs.IsCurveClosed(new_border):
            
            new_border = rs.CloseCurve(new_border, tolerance = sc.doc.ModelAbsoluteTolerance * 2)
            print( "OK, closed using rs.close")
    except Exception as e:
        print (e)
        try:
            rs.UnselectAllObjects()
            rs.SelectObject(new_border)
            rs.Command("!_CloseCrv -Enter -Enter")
            print ("OK, closed using rs.comand")
        except Exception as e:
            print (e)
            """
            RHINO_FORMS.notification(main_text = "The offset cannot be closed, your geometry might have some issue. Please process this manually..",
                                        sub_text = "I am going to flash it for you so you know which I am talking about..",
                                        height = 300)
            """
            # NOTIFICATION.messenger(main_text = "The offset cannot be closed, your geometry might have some issue.\nPlease process this manually..",)
            rs.AddTextDot("This surface cannot get a closed crv after offset.\nPlease process this guy manually.", RHINO_OBJ_DATA.get_center(srf))
            rs.DeleteObjects([border])
            RHINO_SELECTION.pay_attention(srf)
            COLOR.invert_color(srf)

            return srf
    
    # new_border = new_border[0]

    # print new_border
    if not rs.IsCurveClosed(new_border):
        rs.AddTextDot("Cannot get a closed crv after offset.\nPlease process this guy manually.", RHINO_OBJ_DATA.get_center(srf))

        # RHINO_FORMS.notification(main_text = "Cannot get a closed crv after offset, your geometry might have some issue. Skip.",
        #                             sub_text = "I am going to flash it for you so you know which I am talking about..",
        #                             height = 300)

        rs.DeleteObjects([border])
        RHINO_SELECTION.pay_attention(srf)
        COLOR.invert_color(srf)

        return srf


    if offset > 0:
        return process_surf_shrinking(srf, border, new_border, offset)
    return process_surf_expanding(srf, border, new_border, offset)


def process_surf_shrinking(srf, border, new_border, offset):

    rs.MoveObject(new_border, [0,0,-50])
    path = rs.AddLine([0,0,0], [0,0,100])
    trimmer = rs.ExtrudeCurve(new_border, path)
    res = rs.SplitBrep(srf, trimmer, delete_input = True)
    inner, ring = sorted(res, key = lambda x: total_prim_length(x))
    trash = [border, path, new_border, trimmer, ring]
    rs.DeleteObjects(trash)
    return inner



def process_surf_expanding(srf, border, new_border, offset):


    loop = rs.AddPlanarSrf([border, new_border])
    temp_ploy_surf = rs.JoinSurfaces([loop, srf], delete_input = True)
    rs.UnselectAllObjects()
    rs.SelectObject(temp_ploy_surf)
    rs.Command("_mergeallfaces _enter", echo = False)
    trash = [border, new_border]
    rs.DeleteObjects(trash)
    return temp_ploy_surf


def offset_floor_border():
        # get objs:
    objs = rs.GetObjects("Get slabs for treatment, accepting srf or polysurf.", preselect = True, filter = 8 + 16)#srf and poly srf
    if not objs:
        NOTIFICATION.toast(main_text = "Nothing is selected.", sub_text = "Cancel")
        return
    #print objs
    objs = filter(lambda x: rs.IsPolysurface(x) or rs.IsSurface(x), objs)


    if not objs or len(objs) == 0:
        NOTIFICATION.toast(main_text = "Cannot find surface or polysurface.", sub_text = "Cancel")
        return

    offset = DATA_FILE.get_sticky_longterm("SLAB_OFFSET_DIST", 300)
    res = rs.PropertyListBox(["Offset inward(model unit):"], [offset], message = "Positive number = shrink. Negative number = expand.", title = "EnneadTab floor shrinker/expander")
    if not res:
        NOTIFICATION.toast(main_text = "Need to have valid input.", sub_text = "Cancel")
        return
    offset = float(res[0])
    DATA_FILE.set_sticky_longterm("SLAB_OFFSET_DIST", offset)

    #print offset
    rs.EnableRedraw(False)

    if offset == 0.0:
        return

    rs.StatusBarProgressMeterShow(label = "Processing {} objs.".format(len(objs)),
                                lower = 0,
                                upper = len(objs),
                                embed_label = True,
                                show_percent = True)
    # check srf or polysurf
    for i,obj in enumerate(objs):
        rs.StatusBarProgressMeterUpdate(position = i, absolute = True)
        original_layer = rs.ObjectLayer(obj)
        try:
            if rs.IsPolysurface(obj):
                new_obj = process_polysurf(obj, offset)
            else:
                new_obj = process_surf(obj, offset)
        except Exception as e:
            RHINO_FORMS.notification(main_text = "Something wrong with one of the selected objects. " + str(e), 
                                     sub_text = traceback.format_exc(), 
                                     height = 500)
            continue

        rs.ObjectLayer(new_obj, original_layer)
        
    NOTIFICATION.messenger(main_text = "Action Completed.")
    rs.StatusBarProgressMeterHide()




