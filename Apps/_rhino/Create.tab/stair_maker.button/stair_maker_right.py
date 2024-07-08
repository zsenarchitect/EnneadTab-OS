
__title__ = "StairMaker(Spiral)"
__doc__ = "Interactively create spiral stair."

import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System # pyright: ignore
import traceback
import math

from EnneadTab import DATA_FILE, NOTIFICATION, LOG, ERROR_HANDLE


def make_stair_mass_brep(e, center_pt, start_pt, end_pt, max_riser, stair_width, thread_thickness, current_pt = None):
    tolerance = sc.doc.ModelAbsoluteTolerance
    # max_riser, stair_width = 170, 2000
    show_internal = False


    radius = rs.Distance([center_pt[0], center_pt[1], 0], [start_pt[0], start_pt[1], 0])
    angle = rs.Angle2([center_pt[0], center_pt[1], 0, start_pt[0], start_pt[1], 0],
                      [center_pt[0], center_pt[1], 0, end_pt[0], end_pt[1], 0])[0]
    #print angle

    #calcuate steps riser and thread by vectical dist/max riser height, horitiontal dist/ step count
    vertical_diff = end_pt[2] - start_pt[2]
    #print vertical_diff
    if vertical_diff < 0.001:
        #print "cancel"
        return (None, None)
    num_of_step = int(math.ceil(vertical_diff / max_riser))
    if num_of_step > 30:
        note = "Check your unit, the riser info might not make sense now.\nYou are trying to create {} steps".format(num_of_step)
        # NOTIFICATION.messenger(main_text = note)
        return (None, note)
    
    
    x0 = [start_pt[0], start_pt[1], 0]
    x1 = [center_pt[0], center_pt[1], 0]

    local_x = rs.VectorCreate(x0, x1)
    
    thread_end_pt = rs.PointAdd(start_pt, stair_width * rs.VectorUnitize(local_x))
    thread_line = Rhino.Geometry.Line(start_pt[0], start_pt[1], start_pt[2], 
                                      thread_end_pt[0], thread_end_pt[1], thread_end_pt[2])
    # thread_line = rs.AddLine(start_pt, rs.PointAdd(start_pt, stair_width * rs.VectorUnitize(local_x)))
    axis = Rhino.Geometry.Line(center_pt[0], center_pt[1], 0, 
                                      center_pt[0], center_pt[1], 1)
    thread_srf = Rhino.Geometry.RevSurface.Create(thread_line, 
                                                  axis, 
                                                  startAngleRadians = 0, 
                                                  endAngleRadians = math.radians(angle/num_of_step))
    thread_srf = thread_srf.ToBrep ()
    
    # thread_srf = rs.AddRevSrf(thread_line, 
    #                           [center_pt[0], center_pt[1], 0, center_pt[0], center_pt[1], 1], 
    #                           start_angle=0.0, 
    #                           end_angle=angle/num_of_step)


    horitiontal_diff = rs.Distance(x0, x1)
    #print vertical_diff
    #print horitiontal_diff
    actual_riser = vertical_diff / num_of_step
    actual_thread = horitiontal_diff / num_of_step


    #print num_of_step, actual_riser, actual_thread

    # create single tread
    distance = -thread_thickness
    both_sides = False
    create_solid = True
    thread_brep = Rhino.Geometry.Brep.CreateFromOffsetFace(thread_srf.Faces[0], distance, tolerance, both_sides, create_solid)
    
    if not thread_brep:
        return (None, "Cannot make preview stair")
    steps = [thread_brep.Duplicate() for i in range(num_of_step)]
    #print steps
    for i in range(num_of_step ):
        steps[i].Rotate(math.radians(i*angle/num_of_step), 
                         Rhino.Geometry.Vector3d(0,0, 1), 
                        Rhino.Geometry.Point3d(center_pt[0], center_pt[1], center_pt[2])) 
        steps[i].Translate(Rhino.Geometry.Vector3d(0,0,actual_riser * i))
    
    note = "Actual Riser = {:.2f}\nNum of Step = {}".format(actual_riser, num_of_step)
    return (steps, note)


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def stair_maker():
    max_riser, stair_width, thread_thickness = DATA_FILE.get_sticky_longterm("STAIR_SPIRAL_MAX_RISER", 170),DATA_FILE.get_sticky_longterm("STAIR_SPIRAL_RISER", 2000), DATA_FILE.get_sticky_longterm("STAIR_SPIRAL_THREAD_THICKNESS", 50)
    res = rs.PropertyListBox(items = ["Max Riser Height(file unit)", "Run Width(file unit)", "Thread Thickness(file unit)"],
                            values = [max_riser, stair_width, thread_thickness],
                            message = "Enter stair primitive data",
                            title = "Stair Maker")
    if not res:
        return
    max_riser, stair_width, thread_thickness = res
    #max_riser = rs.RealBox(message = "Max riser height number", default_number = 170, title = "EnneadTab")
    max_riser, stair_width, thread_thickness = float(max_riser), float(stair_width), float(thread_thickness)
    DATA_FILE.set_sticky_longterm("STAIR_SPIRAL_MAX_RISER", max_riser)
    DATA_FILE.set_sticky_longterm("STAIR_SPIRAL_RISER", stair_width)
    DATA_FILE.set_sticky_longterm("STAIR_SPIRAL_THREAD_THICKNESS", thread_thickness)


    get_pt_instance = Rhino.Input.Custom.GetPoint()
    get_pt_instance.SetCommandPrompt("Stair Spiral Center Pt")
    get_pt_instance.Get()
    if get_pt_instance.CommandResult() != Rhino.Commands.Result.Success:
        return get_pt_instance.CommandResult()
    center_pt = get_pt_instance.Point()
    if center_pt == Rhino.Geometry.Point3d.Unset:
        return Rhino.Result.Failure

    get_pt_instance = Rhino.Input.Custom.GetPoint()
    get_pt_instance.SetCommandPrompt("Stair Start Pt(Inner Bound)")
    get_pt_instance.Get()
    if get_pt_instance.CommandResult() != Rhino.Commands.Result.Success:
        return get_pt_instance.CommandResult()
    start_pt = get_pt_instance.Point()
    if start_pt == Rhino.Geometry.Point3d.Unset:
        return Rhino.Result.Failure

    get_dot_pt_instance = GetDotPoint(center_pt, start_pt, max_riser, stair_width, thread_thickness)
    get_dot_pt_instance.SetCommandPrompt("Stair End Pt")
    get_dot_pt_instance.ConstrainToConstructionPlane(False)
    get_dot_pt_instance.SetBasePoint(start_pt, True)
    get_dot_pt_instance.DrawLineFromPoint(start_pt, True)
    get_dot_pt_instance.Get()
    if get_dot_pt_instance.CommandResult() != Rhino.Commands.Result.Success:
        return get_dot_pt_instance.CommandResult()
    end_pt = get_dot_pt_instance.Point()
    if end_pt == Rhino.Geometry.Point3d.Unset:
        return Rhino.Result.Failure

    if end_pt[2] == start_pt[2]:
        return


    

    if center_pt is None:
        NOTIFICATION.messenger("Center Pt is not valid")
        return
    if not start_pt:
        NOTIFICATION.messenger("Start Pt is not valid")
        return
    if not end_pt:
        NOTIFICATION.messenger("End Pt is not valid.")
        return
    
    mass_breps, note = make_stair_mass_brep("e", center_pt, start_pt, end_pt, max_riser, stair_width, thread_thickness)
    # print mass_breps
    if not mass_breps:
        NOTIFICATION.messenger("Invalid input")
        return
    new_objs = [sc.doc.Objects.AddBrep(mass_brep) for mass_brep in mass_breps]
    rs.AddObjectsToGroup(new_objs, rs.AddGroup())
    sc.doc.Views.Redraw()
    # print new_objs
    #create_stair_block_from_pts(center_pt, start_pt, end_pt, max_riser, stair_width, flip_pt )
 



class GetDotPoint (Rhino.Input.Custom.GetPoint):
    """Stemp 1"""
    def __init__(self, center_pt, start_pt, max_riser, stair_width, thread_thickness):
        self.center_pt = center_pt
        self.start_pt = start_pt
        self.max_riser = max_riser
        self.thread_thickness = thread_thickness
        self.stair_width = stair_width
        self.default_color = rs.CreateColor([87, 85, 83])
        #self.viewport = sc.doc.Views.ActiveView.ActiveViewport
    #@ERROR_HANDLE.try_catch_error


    def show_text_with_pointer(self, e, text, size, color = None, is_middle_justified = False):
        if not color:
            color = self.default_color
        e.Display.Draw2dText(text, color, self.pointer_2d, is_middle_justified, size)
        #self.pointer_2d = Rhino.Geometry.Point2d(self.pointer_2d[0], self.pointer_2d[0] + size - 5)
        self.pointer_2d += Rhino.Geometry.Vector2d(0, size )


    def OnDynamicDraw(self, e):

        position_X_offset = 20
        position_Y_offset = 40
        bounds = e.Viewport.Bounds
        self.pointer_2d = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)


        end_pt = e.CurrentPoint


        try:
            mass_breps, note = make_stair_mass_brep(e, self.center_pt, self.start_pt, end_pt, self.max_riser, self.stair_width, self.thread_thickness)
            if mass_breps:
                for mass_brep in mass_breps:
                    e.Display.DrawBrepWires  (mass_brep, System.Drawing.Color.White, -1)
                    e.Display.DrawBrepShaded (mass_brep, Rhino.Display.DisplayMaterial(System.Drawing.Color.Blue, 0))


            #e.Display.DrawToBitmap (self.viewport, 300, 200)
        except:
            print (traceback.format_exc())

        if mass_brep:
            bbox = mass_brep.GetBoundingBox(False)
            data_pt = (bbox.Min + bbox.Max)/2
        else:
            data_pt = (self.start_pt + end_pt)/2
        e.Display.DrawDot  (data_pt, note)


        title = "EnneadTab Stair Maker Mode -- Preview Stair"
        self.show_text_with_pointer(e,
                                    text = title,
                                    size = 30)

        e.Display.DrawDot  (self.center_pt, "Center Pt")
        e.Display.DrawDot  (self.start_pt, "Start Pt(Inner bound)")



        if end_pt[2] - self.start_pt[2] > 0.001:
            e.Display.DrawDot  (end_pt, "End Pt")
            self.show_text_with_pointer(e,
                                        text = note,
                                        size = 15)
        else:
            e.Display.DrawDot  (end_pt, "End of stair cannot be on same height as or lower than the start of stair.")
            self.show_text_with_pointer(e,
                                        text = "Your input point does not make sense!!!!!!",
                                        size = 15)




if __name__ == "__main__":
    stair_maker()