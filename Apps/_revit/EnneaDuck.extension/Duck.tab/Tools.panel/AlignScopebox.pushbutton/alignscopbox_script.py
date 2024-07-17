
from pyrevit import revit, DB
from pyrevit import script
from pyrevit import forms
import math

from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE

__doc__ = 'Need at leat one model line as refference, and one scopebox to play with. Becasue the initial oriteation of the scopebox can be unpredicatable so i cannot ganrantee it finish in one go, but by large it can find the angle within 3 clicks.'
__tip__ = True
__title__ = "Orient\nScopebox"
__youtube__ = "https://youtu.be/NBQQd-GXGRQ"

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

def find_angle(vec1,vec2):
    angle = math.degrees(vec1.AngleTo(vec2))
    telorance = 0.0000000001
    if angle < telorance:
        return 0.0
    elif -telorance < angle - 90 < telorance:
        return 90.0
    elif -telorance < angle - 180 < telorance:
        return 180.0
    else:
        return angle

def find_all_angles_scopbox(scopebox, ref_line):
    edges = scopebox.Geometry[DB.Options()]
    angle_list = []
    for edge in edges:

        angle_list.append(find_angle(edge.Direction,ref_line.Direction))
    return angle_list


def is_scopebox_ok(angle_list):
    temp = 1.0
    for angle in angle_list:
        temp *= angle
    if temp == 0.0:

        return True
    else:
        return False

def find_scopebox_center_z_axis(scopebox):
    box = scopebox.Geometry[DB.Options()].GetBoundingBox()

    center = (box.Max + box.Min) / 2
    #print "center is {}".format(center)
    return DB.Line.CreateBound(center,center.Add(DB.XYZ(0,0,1)))


def try_fix(scopeboxs, mode, ref_line):
    for scopebox in scopeboxs:
        #print "new scopebox"
        angle_list = find_all_angles_scopbox(scopebox, ref_line)
        if is_scopebox_ok(angle_list) and mode in  ["default mode A","default mode B"]:
            #print "******Scopebox ok"
            pass
        else:
            #print "####scopebox need rotation"
            #print angle_list

            rotation = min(angle_list)
            #print "rotation is {}".format(rotation)
            axis = find_scopebox_center_z_axis(scopebox)
            if mode == "default mode A":
                DB.ElementTransformUtils.RotateElement(revit.doc, scopebox.Id, axis, -math.radians(rotation))
            if mode == "default mode B":
                DB.ElementTransformUtils.RotateElement(revit.doc, scopebox.Id, axis, math.radians(rotation))
            elif mode == "90 degree mode":
                DB.ElementTransformUtils.RotateElement(revit.doc, scopebox.Id, axis, math.radians(90))
            else:
                print ("conditions no exist")

def update_display_text(scopeboxs):
    scopeboxs_condition_ready = True
    for scopebox in scopeboxs:
        if is_scopebox_ok(find_all_angles_scopbox(scopebox)) == False:
            scopeboxs_condition_ready = False

    if scopeboxs_condition_ready:
        return  "All scopboxs is aligned in at least one direction.\nDo you want to adjusting orientation by 90 degree?"

    else:
        return  "Not all scopeboxs are ready.\nPlease try oritent option continously."

@ERROR_HANDLE.try_catch_error
def main():
    selection = list(revit.get_selection())
    if not selection:
        forms.alert("Please selection some elements first.")
        return

    """
    for x in selection:
        print(x.GetType(),x,x.Category.Name)
    """

    scopeboxs = [x for x in selection if x.Category.Name == "Scope Boxes"]
    ref_lines = [x for x in selection if x.Category.Name == "Lines"]

    if len(scopeboxs) == 0:
        forms.alert("Need at least one scopebox.")
        return
    if len(ref_lines) == 0:
        forms.alert("Need at least one model line as ref line.")
        return

    ref_line = ref_lines[0].GeometryCurve

    with revit.Transaction("Align Scopebox"):
        display_text = "abcdefghijklmn"
        try_fix(scopeboxs,"default mode B", ref_line)
        display_text = update_display_text(scopeboxs)

    while True:
        if  "Not all scopeboxs are ready." in display_text:
            options = ["Try one more time(Clockwise)", "Try one more time(Counter Clockwise)", "Cancel and close"]
        else:
            options = ["Confirm and close", "Rotate 90 degree for all and close","Cancel and close"]

        result = forms.alert(display_text, options = options)

        if result == "Try one more time(Clockwise)":
            with revit.Transaction("Align Scopebox"):
                try_fix(scopeboxs,"default mode A", ref_line)
                display_text = update_display_text(scopeboxs)

        elif result == "Try one more time(Counter Clockwise)":
            with revit.Transaction("Align Scopebox"):
                try_fix(scopeboxs,"default mode B", ref_line)
                display_text = update_display_text(scopeboxs)

        elif result == "Confirm and close":
            break

        elif "Rotate 90 degree for all" in result:
            with revit.Transaction("Align Scopebox"):
                try_fix(scopeboxs,"90 degree mode", ref_line)
       

        else:#cancelled click
            return

#################################

if __name__ == "__main__":
    main()