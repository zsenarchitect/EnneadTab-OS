#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Resize wall tags leader length to a user defined model space distance."
__title__ = "resize_wall_tags"

from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import clr
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def project_pt_in_view(pt, view):
    z = view.ViewDirection
    origin = view.Origin

    project_vec = (pt - origin).DotProduct(z) * z
    return pt - project_vec
    """
    plane = DB.Plane.CreateByNormalAndOrigin (z, origin)
    uv = clr.StrongBox[DB.UV](DB.UV(0,0))
    dist = clr.StrongBox[float](0.0)
    return plane.Project(pt, uv, dist)
    """

def process_tag(tag, max_length):
    view = doc.GetElement(tag.OwnerViewId)


    original_condition = tag.LeaderEndCondition
    tag.LeaderEndCondition = DB.LeaderEndCondition.Free
    end = tag.LeaderEnd
    tag.LeaderEndCondition = original_condition
    end = project_pt_in_view(end, view)




    head = tag.TagHeadPosition
    head = project_pt_in_view(head, view)


    current_length = end.DistanceTo (head)
    if current_length < max_length:
        return


    if tag.HasElbow :
        vec = head - end
        original_length = vec.GetLength()
        elbow = tag.LeaderElbow
        elbow = project_pt_in_view(elbow, view)
        vec = elbow - end
        vec = vec.Normalize () * (max_length * (vec.GetLength () / original_length))
        new_elbow_location  = end + vec

    vec = head - end
    original_length = vec.GetLength()
    vec = vec.Normalize () * max_length
    tag.TagHeadPosition  = end + vec

    if tag.HasElbow :
        tag.LeaderElbow  = new_elbow_location

def process_view(view, max_length):
    independent_tags = DB.FilteredElementCollector(doc, view.Id).OfClass(DB.IndependentTag).WhereElementIsNotElementType().ToElements()

    # for x in independent_tags:
    #     print x.Category.Name

    wall_tags = filter(lambda x:  x.Category.Name == "Wall Tags", independent_tags)
    max_length *= view.Scale
    map(lambda x: process_tag(x, max_length), wall_tags)


def resize_wall_tags():
    pass
    views = forms.select_views(multiple = True)
    if not views:
        return

    while True:
        max_length = forms.ask_for_string(prompt = "In paper space, in inch unit, what is the max allowed leader length?\nAn extra 0.13inch will be added on top automatically,\nso to offset the head symbol size.", default = "0.75", width = 1500)
        try:
            max_length = (float(max_length ) + 0.13)/ 12.0# convert inch to feet
            break
        except:
            pass


    t = DB.Transaction(doc, __title__)
    t.Start()
    map(lambda x:process_view(x, max_length), views)
    t.Commit()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    resize_wall_tags()
    










