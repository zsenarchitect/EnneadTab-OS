#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Get the GUID for current model. This is the identifier on BIM360 server."
__title__ = "63_Get model GUID"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def get_guid():
    print(doc.Title)
    model_path = doc.GetWorksharingCentralModelPath ()
    print(model_path.GetModelGUID ())
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    get_guid()
