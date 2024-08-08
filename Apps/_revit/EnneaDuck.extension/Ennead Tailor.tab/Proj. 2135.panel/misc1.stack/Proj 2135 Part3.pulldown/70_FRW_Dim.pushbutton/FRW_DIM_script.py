#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "NOT IN USE, attemp to auto dimension distence between FRW windows"
__title__ = "70_FRW Dims(NOT IN USE)"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def get_adj_FRW(family_instance, search_pool):
    my_location = family_instance.Location.Point
    OUT = []
    for other_instance in search_pool:
        if other_instance.Id == family_instance.Id:
            continue
        other_location = other_instance.Location.Point
        dist = my_location.DistanceTo(other_location)
        OUT.append((other_instance, dist))

    OUT.sort(key = lambda x: x[1])
    adj_instance_list = [x[0] for x in OUT]
    print(OUT)
    return adj_instance_list

def dim_FRW():
    # in current view, get all FRW
    GMs = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    FRWs = filter(lambda x: x.Symbol.FamilyName == "FRW_Main Shared", GMs)
    #print FRWs

    # for each FRW, get location point and two other close to it
    exisiting_pair = []
    for FRW in FRWs:
        print("$" * 20)


        adj_FRWs = get_adj_FRW(FRW, FRWs)

        # for each pair of family instance, "GetReferences(IList Ref type" to get CenterLeftRight refs
        for i, other_FRW in enumerate(adj_FRWs):
            print(exisiting_pair)
            if i == 2:
                break
            if sorted([other_FRW.Id, FRW.Id]) in exisiting_pair:
                continue
            refs = DB.ReferenceArray()

            """
            refs.Append(FRW.GetReferences(DB.FamilyInstanceReferenceType.CenterLeftRight )[0])
            refs.Append(other_FRW.GetReferences(DB.FamilyInstanceReferenceType.CenterLeftRight)[0])
            """
            refs.Append(FRW.GetReferenceByName ("Center (Left/Right)"))
            refs.Append(other_FRW.GetReferenceByName ("Center (Left/Right)"))

            line = DB.Line.CreateBound( FRW.Location.Point, other_FRW.Location.Point)
            # create dimension using line, and references
            try:
                dim = doc.Create.NewDimension(doc.ActiveView, line, refs)

                DB.ElementTransformUtils.MoveElement(doc, dim.Id, DB.XYZ(0,0,1))
                exisiting_pair.append(sorted([other_FRW.Id, FRW.Id]))
                if len(exisiting_pair) == 2:
                    break
            except:
                pass
    pass
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    t = DB.Transaction(doc, "dim FRW")
    t.Start()
    dim_FRW()
    t.Commit()
