
__title__ = "SrfToPanel"
__doc__ = "Convert well defined panelization of surfs to detailed polysrfs with thickness, joint reveal to edge."


import rhinoscriptsyntax as rs
import time


from EnneadTab import NOTIFICATION, DATA_FILE

def srf_to_panel():
    srfs = rs.GetObjects("get base srfs", preselect = True, filter=rs.filter.surface)
    if not srfs:
        return

    PanelMaker(srfs).make_panels()

class PanelMaker:
    def __init__(self, srfs):
        self.srfs = srfs
        self.is_valid = True

        default_thickness = DATA_FILE.get_sticky_longterm("SRF2PANEL_THICKNESS", 50)
        default_joint_width = DATA_FILE.get_sticky_longterm("SRF2PANEL_JOINT_WIDTH", 7.5)
        res = rs.PropertyListBox(["Panel Overall Thickness", "Joint Width"],
                                [default_thickness, default_joint_width],
                                "Enter Panel Dimensions")
        if not res:
            self.is_valid = False
            return

        try:
            self.overall_thickness = float(res[0])
            self.open_joint_width = self.open_joint_depth = float(res[1])
        except:
            self.is_valid = False
            return

    def make_panels(self):
        if not self.is_valid:
            return
        self.collection = []   
        self.trash = [] 
        rs.EnableRedraw(False)
        self.starting_time = time.time()
        self.counter = 0
        map(self.process_srf, self.srfs)


        rs.DeleteObjects(self.trash)

        rs.AddObjectsToGroup(self.collection, rs.AddGroup())
        end = time.time()
        used_time = end - self.starting_time
        rs.Command("savesmall")
        rs.MessageBox("time used = {} seconds = {}mins".format(used_time, used_time/60))

        DATA_FILE.set_sticky_longterm("SRF2PANEL_THICKNESS", self.overall_thickness)
        DATA_FILE.set_sticky_longterm("SRF2PANEL_JOINT_WIDTH", self.open_joint_width)


    def process_srf(self, srf):

        self.counter += 1
        if self.counter % 10 == 0:
            print ("{}/{}".format(self.counter, len(self.srfs)))
        
        first_ref_face_A = rs.OffsetSurface(srf, -self.open_joint_width)
        first_ref_face_B = rs.OffsetSurface(srf, self.open_joint_width)
        back_solid = rs.OffsetSurface(first_ref_face_A, -(self.overall_thickness - self.open_joint_width), create_solid = True)



        border = rs.DuplicateSurfaceBorder(srf, type = 0)
        
        offseted_border = rs.OffsetCurveOnSurface(border, srf, -self.open_joint_width)

        # print (offseted_border)
        if not offseted_border:
            # print ("try altenative")
  
            rs.UnselectAllObjects()
            rs.SelectObjects([srf, border])
            rs.Command("NoEcho OffsetCrvOnSrf  {} _enter".format(self.open_joint_width))
            rs.UnselectAllObjects()
            offseted_border = rs.LastCreatedObjects()


        # i am using this enlongated method because the API method is not always stable, sometime give bad result... reason unknown
        projected_offset_crv_A = rs.PullCurve(first_ref_face_A, offseted_border)
        if len(projected_offset_crv_A) != 1:
            projected_offset_crv_A = rs.JoinCurves(projected_offset_crv_A, delete_input = True)
        projected_offset_crv_B = rs.PullCurve(first_ref_face_B, offseted_border)
        if len(projected_offset_crv_B) != 1:
            projected_offset_crv_B = rs.JoinCurves(projected_offset_crv_B, delete_input = True)

        self.trash.extend([first_ref_face_A, first_ref_face_B])
        # rs.DeleteObjects([first_ref_face_A, first_ref_face_B])
        extruded_cutter = rs.AddLoftSrf((projected_offset_crv_A, projected_offset_crv_B))

        cuts = rs.SplitBrep(srf, extruded_cutter, delete_input = False)
        if cuts:
            cuts.sort(key = lambda x: rs.Area(x))
            true_shape = cuts[1]
            # rs.DeleteObject(cuts[0])
            # rs.DeleteObject(extruded_cutter)
            # rs.DeleteObjects([projected_offset_crv_A, projected_offset_crv_B, offseted_border, border])
            self.trash.extend([cuts[0], extruded_cutter, projected_offset_crv_A, projected_offset_crv_B, offseted_border, border])
        else:
            rs.ObjectColor(extruded_cutter, color = rs.CreateColor(250,10,10))
            NOTIFICATION.messenger(main_text = "failed process color as red")
            return

        outter_solid = rs.OffsetSurface(true_shape, -(self.open_joint_depth *1.05), create_solid = True)
        # rs.DeleteObject(true_shape)
        self.trash.append(true_shape)


        
        final = rs.BooleanUnion([outter_solid, back_solid])
        try:
            rs.ShrinkTrimmedSurface(final)
            self.collection.append(final)
        except Exception as e:
            NOTIFICATION.messenger(main_text = "Cannot shrink surface")
        

