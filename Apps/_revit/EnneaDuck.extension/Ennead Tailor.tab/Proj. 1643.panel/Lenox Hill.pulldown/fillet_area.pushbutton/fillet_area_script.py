#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Fillet Area Corner"

# from pyrevit import forms #

from pyrevit import script #
import math
import clr
import ENNEAD_LOG
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = EnneadTab.REVIT.REVIT_APPLICATION.get_doc()


RADIUS = 1


@EnneadTab.ERROR_HANDLE.try_catch_error
def fillet_area():
    t = DB.Transaction(doc, __title__)
    t.Start()


    
    areas = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Areas).ToElements()
    option = DB.SpatialElementBoundaryOptions ()
    
    for i, area in enumerate(areas):
        fillet_arcs = []
        print (i)
        border_loops = area.GetBoundarySegments (option)
        for border_loop in border_loops:
            curves = [x.GetCurve() for x in border_loop]
            corners = [x.GetEndPoint(0) for x in curves]
            
            for corner in corners:
                print(corner.X, corner.Y, corner.Z)
                
                plane = DB.Plane.CreateByNormalAndOrigin(doc.ActiveView.ViewDirection,corner)
                circle = DB.Arc.Create(plane, RADIUS, 0, 2*math.pi)

                neighbors = []
                for other_crv in curves:
                    res = circle.Intersect(other_crv)
                    if res == DB.SetComparisonResult.Overlap:


                        iResult = clr.StrongBox[DB.IntersectionResultArray](DB.IntersectionResultArray())
                        circle.Intersect(other_crv,iResult)
                        if iResult.Size > 1:
                            print( "%%%%many intersection. Have {} intersection".format(iResult.Size))
                        else:
                            # print (iResult.Size)
                            pass


                        neighbors.append(iResult.Item[0].XYZPoint)
                        
                    else:
                        print(res)


                if len(neighbors) != 2:
                    print("should be 2 exact neiborsss. hereare the neigboss:\n{}".format(neighbors))
                    continue
                for int_x in neighbors:
                    print(int_x.X, int_x.Y, int_x.Z)



                
                fillet_arc = DB.Arc.Create(neighbors[0], neighbors[1], corner)

                
                # print pts
                pts = [neighbors[0], corner, neighbors[1]]
                # print pt_count
                pts = EnneadTab.DATA_CONVERSION.list_to_system_list(pts, type = "XYZ", use_IList = False)

                weights = [1.0, 0.707106781186548,1.0] 
                # print weights
                weights = EnneadTab.DATA_CONVERSION.list_to_system_list(weights, type = "Double", use_IList = False)
                fillet_arc = DB.NurbSpline.CreateCurve(pts, weights)


                
                fillet_arcs.append(fillet_arc)

        level_id = doc.ActiveView.GenLevel.Id
        sketch_plane = DB.SketchPlane.Create(doc, level_id)
        new_area_boundaries = [doc.Create.NewAreaBoundaryLine (sketch_plane, crv, doc.ActiveView) for crv in fillet_arcs]



        new_element_ids = [x.Id for x in new_area_boundaries]

        group = doc.Create.NewGroup(EnneadTab.DATA_CONVERSION.list_to_system_list(new_element_ids))

        group.GroupType.Name = "Rounded Area_({}_{})".format(doc.ActiveView.Name,
                                                                            EnneadTab.TIME.get_formatted_current_time())




        


    t.Commit()



################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    fillet_area()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







