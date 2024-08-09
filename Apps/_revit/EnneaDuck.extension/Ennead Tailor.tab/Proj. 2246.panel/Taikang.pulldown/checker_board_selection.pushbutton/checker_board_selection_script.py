#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Get checker board A/B selection from the curtain wall, requested by Furui"
__title__ = "Checker Board Selection"

# from pyrevit import forms #
from pyrevit import script #
import clr

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
            
@EnneadTab.ERROR_HANDLE.try_catch_error()
def checker_board_selection():
    selection = EnneadTab.REVIT.REVIT_SELECTION.get_selection()
    if len(selection) == 0:
        EnneadTab.NOTIFICATION.messenger(main_text = "Nothing selected")
        return
    mode_opts = ["A collection",
                 "B collection"]
    res = EnneadTab.REVIT.REVIT_FORMS.dialogue(options = mode_opts,
                                               main_text = "Which kind of selection?")
    is_alt_mode = res == mode_opts[1]
    
    
    walls = filter(lambda x: x.Category.Name == "Walls", selection)
    panels = []
    for wall in walls:
        grids = wall.CurtainGrid
        
        u_grids = [x.IntegerValue for x in wall.CurtainGrid.GetUGridLineIds()]
        v_grids = [x.IntegerValue for x in wall.CurtainGrid.GetVGridLineIds()]
        #print grids
        #print grids.GetVGridLineIds()
        """
        for Vgrid in grids.GetVGridLineIds():
            print(revit.doc.GetElement(Vgrid).FullCurve.GetEndPoint(0))
        """

        panel_collection = [ doc.GetElement(x) for x in wall.CurtainGrid.GetPanelIds()]

        # # print panel_collection
        for panel in panel_collection:
   
            u_grid_id = clr.StrongBox[DB.ElementId](DB.ElementId(1))
            v_grid_id = clr.StrongBox[DB.ElementId](DB.ElementId(2))
            panel.GetRefGridLines (u_grid_id, v_grid_id)
            # print (output.linkify(u_grid_id))
            # print (output.linkify(v_grid_id))

            
            u_order = u_grids.index(u_grid_id.IntegerValue) + 1 if u_grid_id.IntegerValue != -1 else 0
            v_order = v_grids.index(v_grid_id.IntegerValue) + 1 if v_grid_id.IntegerValue != -1 else 0
            
            is_selecting = (v_order - u_order)%2
            if is_alt_mode:
                is_selecting = not is_selecting
                
            if is_selecting:
                panels.append(panel)

        """
        for i,U in enumerate(grids.GetUGridLineIds()):
            for j,V in enumerate(grids.GetVGridLineIds()):
                if is_alt_mode:
                    if i % 2 == j % 2 :
                        continue
                else:
                    if i % 2 != j % 2 :
                        continue
                panel = grids.GetPanel(U, V)
                # print "\n\n"
                # print i
                # print j
                panels.append( panel)
                
        """
          
    
    
    EnneadTab.REVIT.REVIT_SELECTION.set_selection(panels)
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    checker_board_selection()
    


