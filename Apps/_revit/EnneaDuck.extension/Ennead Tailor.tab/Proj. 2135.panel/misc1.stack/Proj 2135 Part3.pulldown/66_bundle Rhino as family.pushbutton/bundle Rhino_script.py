#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "NOT IN USE"
__title__ = "66_bundle Rhino(NOT IN USE)"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def bundle_rhino():
    pass
    # pick rhinos

    #pick total bundle family name

    #for each rhino, create new family, load into, assign subC, make it shared? load to containner famiy, move to origion

    #load the container family to project
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    bundle_rhino()
