#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Expand or shrink view crop on multiple viewports."
__title__ = "Offset View Crop"

from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
uidoc = __revit__.ActiveUIDocument


def offset_view_crop():
    #offset = forms.ask_for_number_slider(default = 1, min = -3, max = 3, prompt = "How much to grow the cropbox boundary? Negative to shrink. Unit in feet in model space.", title = "Viewport Border Offset")
    offset = forms.ask_for_string(default = str(1), prompt = "Cropbox offset? Negative to shrink. Unit in feet in model space.", title = "Viewport Border Offset")
    try:
        offset = float(offset)
    except:
        print("cannot convert this number")
        return
    selection_ids = uidoc.Selection.GetElementIds ()
    selection = [doc.GetElement(x) for x in selection_ids]
    selection = filter(lambda x: type(x) == DB.Viewport, selection)


    # move each viewport by diff amount
    t = DB.Transaction(doc, __title__)
    t.Start()
    for viewport in selection:

        view_id = viewport.ViewId
        view = doc.GetElement(view_id)
        boundary = view.GetCropRegionShapeManager()
        crv_loop = boundary.GetCropShape ()# return a curveloop
        new_crv_loop = DB.CurveLoop.CreateViaOffset (crv_loop[0], -offset, view.ViewDirection )
        boundary.SetCropShape (new_crv_loop)




    t.Commit()
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    offset_view_crop()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
