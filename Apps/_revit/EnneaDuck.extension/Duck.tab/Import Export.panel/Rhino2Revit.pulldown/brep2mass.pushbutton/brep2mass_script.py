#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Based on the brep data exported from EnneadTab for Rhino, create adaptive mass shape as native Revit object."
__title__ = "Brep2Mass"
__tip__ = True
from pyrevit import forms #
from pyrevit import script #

import traceback
import ENNEAD_LOG

from EnneadTab.REVIT import REVIT_UNIT, REVIT_APPLICATION
from EnneadTab import SOUNDS, DATA_FILE, FOLDER, ERROR_HANDLE
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
app = __revit__.Application





class Solution:
    def __init__(self):
        self.unit = REVIT_UNIT.pick_incoming_file_unit()
        if self.unit is None:
            return
        
        
    @ERROR_HANDLE.try_catch_error
    def main(self, brep_data):

        print(brep_data)

    
        t = DB.Transaction(doc, 'Create simple cap.')
    
        t.Start()
        #Define cap form corners XYZ to define plane corners
        # p1 = DB.XYZ(5,0,0)
        # p2 = DB.XYZ(20,0,5)
        # p3 = DB.XYZ(20,20,10)
        # p4 = DB.XYZ(0,20,0)
        # p5 = DB.XYZ(-10,20,10)
        # p6 = DB.XYZ(-10,0,0)


        #self.vertex = [doc.FamilyCreate.NewReferencePoint(pt) for pt in [p1, p2, p3, p4]]
        self.vertex = [] 


        for i, pt_list in brep_data.items():
            pt_list = [self.make_revit_pt(x) for x in pt_list]
            try:
                self.cap_by_pts(pt_list)
            except:
                print (traceback.format_exc())



        #caps = [self.cap_by_pts([p1, p2, p3]), self.cap_by_pts([p3, p4, p1]), self.cap_by_pts([p1, p4, p5]), self.cap_by_pts([p5, p6, p1])]

  

        for ver in self.vertex:
            print("{}".format(output.linkify(ver.Id)))
        
        """
        array = DB.CombinableElementArray ()
        for cap in caps:
            array.Append(cap)
        doc.CombineElements(array)
        """

        


        t.Commit()


        SOUNDS.play_sound("sound effect_mario message.wav")
        return

    def make_revit_pt(self, x):

        if self.unit == 0:
                
            X = REVIT_UNIT.mm_to_internal(x[0])
            Y = REVIT_UNIT.mm_to_internal(x[1])
            Z = REVIT_UNIT.mm_to_internal(x[2])
            return DB.XYZ(X, Y, Z)
        elif self.unit == 1:
  
            return DB.XYZ(x[0], x[1], x[2])

    def line_by_pts(self, p1, p2):
        print("---------making new line")
        pt_arry = DB.ReferencePointArray()
        for pt in [p1, p2]:
            for ref_pt in self.vertex:
  
                if ref_pt.Position.IsAlmostEqualTo (pt, 0.001) :
                    pt_arry.Append(ref_pt)
                    print("using exisiting rp point: " + ref_pt.Position.ToString())
                    break
            else:
                new_ref_pt = doc.FamilyCreate.NewReferencePoint(pt)
                print("add new rp point: " + new_ref_pt.Position.ToString())
                self.vertex.append(new_ref_pt)
                print("self.vertex = " + str(self.vertex))
                pt_arry.Append(new_ref_pt)

        """
        for edge in self.edges:
            if edge.GetPoints()[0].Position.IsAlmostEqualTo (p1) and edge.GetPoints()[1].Position.IsAlmostEqualTo (p2):
                return edge
        """

        print("line pt size = " + pt_arry.Size.ToString())
        edge = doc.FamilyCreate.NewCurveByPoints (pt_arry)
        edge.IsReferenceLine = True
  

        return edge
 


    def cap_by_pts(self, pts):
  
        crvs = []
        for i in range(len(pts)-1):
            crvs.append(self.line_by_pts(pts[i], pts[i+1])) 
        #crvs.append(self.line_by_pts(pts[-1], pts[0]))

        
        #create reference array for model curves
        refarr = DB.ReferenceArray()
        for crv in crvs:
            refarr.Append(crv.GeometryCurve.Reference)

        #create cap form
        cap = doc.FamilyCreate.NewFormByCap(True, refarr)

        return cap
   
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":


    solution = Solution()

    file = FOLDER.get_EA_dump_folder_file("BREP2MASS_DATA.json")
    data = DATA_FILE.read_json_as_dict(file)
    for brep_name, brep_data in data.items():
        
        solution.main(brep_data)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)



