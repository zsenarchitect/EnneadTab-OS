#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Align selected viewports to the right handside, with view title coming to right as well."
__title__ = "Align Viewports"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
import ENNEAD_LOG
from Autodesk.Revit import DB # pyright: ignore 
uidoc = __revit__.ActiveUIDocument
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

#def get_max_ptX


def align_viewports():
    pass
    # select viewports
    selection_ids = uidoc.Selection.GetElementIds ()
    selection = [doc.GetElement(x) for x in selection_ids]
    selection = filter(lambda x: type(x) == DB.Viewport, selection)

    opt = ["Align left", "Align right"]
    res = EA_UTILITY.dialogue(options = opt, main_text = "Pick side..")
    if not res:
        return
    if res == opt[0]:
        is_right_align = False
    else:
        is_right_align = True
    # sort boundary right
    outlines = [x.GetBoxOutline() for x in selection]
    #print outlines
    max_pts = [x.MaximumPoint for x in outlines]
    min_pts = [x.MinimumPoint for x in outlines]
    max_right_ptX = max([pt.X for pt in max_pts])
    min_left_ptX = min([pt.X for pt in min_pts])

    #label_outlines = [x.GetLabelOutline () for x in selection]


    """
    try view.CropBox ---> BoundingBoxXYZ
    try view.Outline ---> BoundingBoxUV


    """
    # move each viewport by diff amount
    t = DB.Transaction(doc, __title__)
    t.Start()
    for viewport in selection:
        view_id = viewport.ViewId
        view = doc.GetElement(view_id)
        elements_2D = filter(lambda x: x.ViewSpecific, DB.FilteredElementCollector(doc, view_id).WhereElementIsNotElementType().ToElements())
        elements_levels = DB.FilteredElementCollector(doc, view_id).OfCategory(DB.BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
        elements_2D.extend(elements_levels)
        #print elements_2D
        elements_2D_ids = [x.Id for x in elements_2D]
        view.HideElementsTemporary (EA_UTILITY.list_to_system_list(elements_2D_ids))

        #doc.Regenerate ()

        """
        view_id = viewport.ViewId
        view = doc.GetElement(view_id)
        boundary = view.GetCropRegionShapeManager()
        crvs = list(boundary.GetCropShape ())# return a curveloop
        print(crvs)
        print(crvs[0])
        right_ptX = None
        crvs = crvs[0]
        for crv in crvs:
            if right_ptX is None or crv.GetEndPoint (0).X > right_ptX:
                right_ptX = crv.GetEndPoint (0).X
        """

        if is_right_align:
            right_ptX = viewport.GetBoxOutline().MaximumPoint.X
            diff = DB.XYZ(max_right_ptX - right_ptX ,0,0)
        else:

            left_ptX = viewport.GetBoxOutline().MinimumPoint.X
            diff = DB.XYZ(min_left_ptX - left_ptX ,0,0)
        viewport.SetBoxCenter(viewport.GetBoxCenter() + diff)


        try:
            if is_right_align:
                label_right_ptX = viewport.GetLabelOutline().MaximumPoint.X
                diff = DB.XYZ(max_right_ptX - label_right_ptX ,0,0)
            else:
                label_left_ptX = viewport.GetLabelOutline().MinimumPoint.X
                diff = DB.XYZ(min_left_ptX - label_left_ptX ,0,0)
            #viewport.LabelLineLength
            viewport.LabelOffset += diff
        except:
            print("No view title move for this guy")
        view.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate)
    t.Commit()

"""
def try_catch_error(func):
    def wrapper(*args, **kwargs):
        print("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            return func(*args, **kwargs)
        except Exception as e:
            print(str(e))
            return "Wrapper func for EA Log -- Error: " + str(e)
    return wrapper
"""
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    align_viewports()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
