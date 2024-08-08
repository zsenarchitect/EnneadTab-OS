#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Try to fix stairs that has end with a riser checked."
__title__ = "69_stair_end_with_riser(Fixer)"

# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import sys

sys.path.append(r'L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135 Part3.pulldown\68_stair_end_with_riser.pushbutton')
import stair_end_with_riser_script as STAIR_CHECKER
from Autodesk.Revit import DB # pyright: ignore 
#from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def stair_end_with_riser():

    fix()


def fix():
    t = DB.Transaction(doc, "create stair check view")
    t.Start()
    view = STAIR_CHECKER.make_3D_views_contain_only_stair()
    t.Commit()
    __revit__.ActiveUIDocument.ActiveView = view

    stairs = [doc.GetElement(x) for x in __revit__.ActiveUIDocument.Selection.GetElementIds ()]
    stairs = filter(lambda x: "DB.Architecture.Stairs " in str(x) , stairs)

    if len(stairs) == 0:
        EA_UTILITY.dialogue(main_text = "Need to select at least one stair that you want to make 'end with riser' checked", sub_text = "Stair inside group must be fixed manually.")
        return

    print("{} stairs selected".format(len(stairs)))
    t = DB.Transaction(doc, "fix stair riser condition")
    t.Start()

    for stair in stairs:
        if stair.GroupId.IntegerValue  > 0:
            print(" [Contained in a group.] Cannot modify by script.")
            continue
        view.SetElementOverrides(stair.Id, DB.OverrideGraphicSettings() )

        run_ids = stair.GetStairsRuns ()
        for run_id in run_ids:
            run = doc.GetElement(run_id)
            run.EndsWithRiser = True
                #print "Run is not ending with riser"


    t.Commit()
    print("\n\n Tool finished. Run it again after modifying stairs to keep checking.")


################## main code below #####################
output = script.get_output()
output.close_others()
output.set_width(1000)


if __name__ == "__main__":

    stair_end_with_riser()
