
__title__ = ["StairMaker", 
             "StairMaker(Linear)"]
__doc__ = "Interactively create linear stair."


import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System # pyright: ignore
import traceback
import math



from EnneadTab import DATA_FILE, LOG, ERROR_HANDLE


def create_stair_block_from_pts(start_pt, end_pt, max_riser, stair_width, flip_pt ):

    rs.EnableRedraw(False)


    vector1 = Rhino.Geometry.Point3d(end_pt[0], end_pt[1], 0)-Rhino.Geometry.Point3d(start_pt[0], start_pt[1], 0)
    vector2 =  Rhino.Geometry.Point3d(flip_pt[0], flip_pt[1], 0) - Rhino.Geometry.Point3d(start_pt[0], start_pt[1], 0)
    vec_z = rs.VectorCrossProduct(vector1, vector2)
    #print vec_z

    if vec_z[2] < 0:
        stair_width *= -1


    #calcuate steps riser and thread by vectical dist/max riser height, horitiontal dist/ step count
    vertical_diff = end_pt[2] - start_pt[2]
    # if vertical_diff == 0:
    #     rs.MessageBox("start and end pt should not be on same elevation.")
    #     return
    x0 = [start_pt[0], start_pt[1], 0]
    x1 = [end_pt[0], end_pt[1], 0]

    local_x = rs.VectorCreate(x1, x0)

    local_y = rs.VectorRotate(local_x, 90, [0,0,1])
    horitiontal_diff = rs.Distance(x0, x1)
    # print vertical_diff
    # print horitiontal_diff
    num_of_step = int(math.ceil(vertical_diff / max_riser))
    actual_riser = vertical_diff / num_of_step
    actual_thread = horitiontal_diff / num_of_step
    # print num_of_step, actual_riser, actual_thread

    #create step profile pts list by step riser and thred depth
    step_overlap = 2 * actual_thread
    x0 = [0,0,0]
    x1 = [actual_thread + step_overlap, 0,0]
    x2 = [actual_thread + step_overlap, 0, -actual_riser]
    x3 = [0, 0, -actual_riser]
    pts = [x0, x1, x2, x3]
    pts.append(x0)
    profile = rs.AddPolyline(pts)
    profile_collection = [profile]


    #array those step profile and curve boolean
    direction = rs.VectorCreate([actual_thread, 0, actual_riser], x0)
    for i in range(num_of_step):
        profile = rs.CopyObject(profile, direction)
        profile_collection.append(profile)

    #curve boolean to get slope soffit of satir
    union_profile = rs.CurveBooleanUnion(profile_collection)
    trimmer_crv_pts = []
    insert_pt = rs.MoveObject(rs.AddPoint(x1), [-actual_thread,0,0])
    trimmer_crv_pts.append(rs.CopyObject(insert_pt , direction * (-1)))
    trimmer_crv_pts.append(rs.CopyObject(trimmer_crv_pts[-1] , direction * (i+1)))
    trimmer_crv_pts.append(rs.CopyObject(trimmer_crv_pts[-1] , [5000,0,0]))
    trimmer_crv_pts.append(rs.CopyObject(trimmer_crv_pts[0] , [5000,0,0]))
    trimmer_crv_pts.append(trimmer_crv_pts[0])
    trimmer_crv = rs.AddPolyline(trimmer_crv_pts)
    final_profile = rs.CurveBooleanDifference(union_profile, trimmer_crv)
    rs.DeleteObjects(profile_collection)
    rs.DeleteObjects(trimmer_crv_pts)
    rs.DeleteObjects(trimmer_crv)
    rs.DeleteObject(insert_pt)
    rs.DeleteObject(union_profile)

    #extrude width, and cap
    stair_mass = rs.ExtrudeCurveStraight(final_profile, x0, [0, stair_width, 0])
    rs.DeleteObjects(final_profile)
    rs.CapPlanarHoles(stair_mass)

    #make a block, inclucde dot text for name.
    block_contents = [stair_mass]
    stair_name = "EA_stair"
    all_block_names = rs.BlockNames()
    while True:
        if stair_name not in all_block_names:
            break
        stair_name += "_new"
    rs.AddBlock(block_contents, base_point = x0, name = stair_name, delete_input = True)


    #insert block back at user pick pts
    initial_plane = rs.CreatePlane([0,0,0], x_axis = [1,0,0], y_axis = [0,1,0], ignored = None)
    final_plane = rs.CreatePlane(start_pt, x_axis = local_x, y_axis = local_y, ignored = None)
    # print initial_plane
    # print final_plane
    transform = rs.XformChangeBasis(final_plane,initial_plane)
    #print transform
    #rs.InsertBlock2(stair_name, transform)
    temp_block = rs.InsertBlock(stair_name, [0,0,0])
    rs.TransformObject(temp_block, transform)


def make_stair_mass_brep(e, start_pt, end_pt, max_riser, stair_width, current_pt = None):
    tolerance = sc.doc.ModelAbsoluteTolerance
    # max_riser, stair_width = 170, 2000
    show_internal = False

    #calcuate steps riser and thread by vectical dist/max riser height, horitiontal dist/ step count
    vertical_diff = end_pt[2] - start_pt[2]
    #print vertical_diff
    if vertical_diff < 0.001:
        #print "cancel"
        return (None, None)
    x0 = [start_pt[0], start_pt[1], 0]
    x1 = [end_pt[0], end_pt[1], 0]

    local_x = rs.VectorCreate(x1, x0)

    if current_pt:
        vector1 = Rhino.Geometry.Point3d(end_pt[0], end_pt[1], 0)-Rhino.Geometry.Point3d(start_pt[0], start_pt[1], 0)
        vector2 =  Rhino.Geometry.Point3d(current_pt[0], current_pt[1], 0) - Rhino.Geometry.Point3d(start_pt[0], start_pt[1], 0)
        vec_z = rs.VectorCrossProduct(vector1, vector2)
        #print vec_z

        if vec_z[2] < 0:
            stair_width *= -1


    local_y = rs.VectorRotate(local_x, 90, [0,0,1])
    horitiontal_diff = rs.Distance(x0, x1)
    #print vertical_diff
    #print horitiontal_diff
    num_of_step = int(math.ceil(vertical_diff / max_riser))
    if num_of_step > 30:
        note = "Check your unit, the riser info might not make sense now.\nYou are trying to create {} steps".format(num_of_step)
        # NOTIFICATION.messenger(main_text = note)
        return (None, note)
    actual_riser = vertical_diff / num_of_step
    actual_thread = horitiontal_diff / num_of_step


    #print num_of_step, actual_riser, actual_thread

    #create step profile pts list by step riser and thred depth
    step_overlap = 2 * actual_thread
    x0 = [0,0,0]
    x1 = [actual_thread + step_overlap, 0,0]
    x2 = [actual_thread + step_overlap, 0, -actual_riser]
    x3 = [0, 0, -actual_riser]
    pts = [x0, x1, x2, x3]
    pts.append(x0)
    pts = [Rhino.Geometry.Point3d(x[0], x[1], x[2]) for x in pts]
    #pts = System.Collections.Generic.IList[Rhino.Geometry.Point3d](pts)
    profile = Rhino.Geometry.PolylineCurve (pts)
    profile_collection = [profile]


    if show_internal:
        e.Display.DrawPolyline (pts, System.Drawing.Color.White)

    #array those step profile and curve boolean
    direction = rs.VectorCreate([actual_thread, 0, actual_riser], x0)
    for i in range(num_of_step):
        profile = profile.Duplicate()
        transform = Rhino.Geometry.Transform.Translation(direction)
        profile.Transform(transform)
        profile_collection.append(profile)

        if show_internal:
            e.Display.DrawCurve(profile, System.Drawing.Color.Blue)



    #curve boolean to get slope soffit of satir


    union_profile = Rhino.Geometry.Curve.CreateBooleanUnion(profile_collection, tolerance)
    union_profile = union_profile[0]
    if show_internal:
        e.Display.DrawCurve(union_profile, System.Drawing.Color.Green)



    trimmer_crv_pts = []

    #insert_pt = rs.MoveObject(rs.AddPoint(x1), [-actual_thread,0,0])
    #transform = Rhino.Geometry.Transform.Translation([-actual_thread,0,0])
    #insert_pt = x1.Transform(transform)
    insert_pt = Rhino.Geometry.Point3d(x1[0], x1[1], x1[2]) + Rhino.Geometry.Vector3d (-actual_thread,0,0)


    #trimmer_crv_pts.append(rs.CopyObject(insert_pt , direction * (-1)))
    transform = Rhino.Geometry.Transform.Translation(direction * (-1))
    temp_pt = Rhino.Geometry.Point3d(insert_pt)
    temp_pt.Transform(transform)
    trimmer_crv_pts.append(temp_pt)


    #trimmer_crv_pts.append(rs.CopyObject(trimmer_crv_pts[-1] , direction * (i+1)))
    transform = Rhino.Geometry.Transform.Translation(direction * (i+1))
    temp_pt = Rhino.Geometry.Point3d(trimmer_crv_pts[-1])
    temp_pt.Transform(transform)
    trimmer_crv_pts.append(temp_pt)


    #trimmer_crv_pts.append(rs.CopyObject(trimmer_crv_pts[-1] , [5000,0,0]))
    transform = Rhino.Geometry.Transform.Translation(5000,0,0)
    temp_pt = Rhino.Geometry.Point3d(trimmer_crv_pts[-1])
    temp_pt.Transform(transform)
    trimmer_crv_pts.append(temp_pt)



    #trimmer_crv_pts.append(rs.CopyObject(trimmer_crv_pts[0] , [5000,0,0]))
    transform = Rhino.Geometry.Transform.Translation(5000,0,0)
    temp_pt = Rhino.Geometry.Point3d(trimmer_crv_pts[0])
    temp_pt.Transform(transform)
    trimmer_crv_pts.append(temp_pt)


    #trimmer_crv_pts.append(trimmer_crv_pts[0])
    trimmer_crv_pts.append(trimmer_crv_pts[0])




    #trimmer_crv = rs.AddPolyline(trimmer_crv_pts)
    trimmer_crv = Rhino.Geometry.PolylineCurve (trimmer_crv_pts)
    if show_internal:
        e.Display.DrawCurve(trimmer_crv, System.Drawing.Color.Purple)


    final_profile = Rhino.Geometry.Curve.CreateBooleanDifference (union_profile, trimmer_crv,tolerance)
    final_profile = final_profile[0]
    if show_internal:
        e.Display.DrawCurve(final_profile, System.Drawing.Color.Yellow)



    vec = Rhino.Geometry.Vector3d (0, stair_width, 0) - Rhino.Geometry.Vector3d (x0[0], x0[1], x0[2])
    surface = Rhino.Geometry.Surface.CreateExtrusion(final_profile, vec)
    #e.Display.DrawSurface(surface, System.Drawing.Color.Black, 0)
    stair_mass = Rhino.Geometry.Brep.CreateFromSurface (surface)

    is_cap = False
    if is_cap:
        stair_mass = stair_mass.CapPlanarHoles(tolerance)
        if stair_mass.SolidOrientation == Rhino.Geometry.BrepSolidOrientation.Inward:
            stair_mass.Flip()

    # print list(stair_mass.Surfaces )
    # stair_mass.CreateFromSurface (surface)
    # print list(stair_mass.Surfaces )



    initial_plane = rs.CreatePlane([0,0,0], x_axis = [1,0,0], y_axis = [0,1,0], ignored = None)
    final_plane = rs.CreatePlane(start_pt, x_axis = local_x, y_axis = local_y, ignored = None)

    transform = rs.XformChangeBasis(final_plane,initial_plane)

    stair_mass.Transform(transform)



    note = "Actual Riser = {:.2f}\nActual Thread = {:.2f}\nNum of Step = {}".format(actual_riser, actual_thread, num_of_step)
    #print note
    return (stair_mass, note)


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def stair_maker():
    max_riser, stair_width = DATA_FILE.get_sticky_longterm("MAX_RISER", 170), DATA_FILE.get_sticky_longterm("STAIR_RISER", 2000)
    res = rs.PropertyListBox(items = ["Max Riser Height(file unit)", "Run Width(file unit)"],
                            values = [max_riser, stair_width],
                            message = "Enter stair primitive data",
                            title = "Stair Maker")
    if not res:
        return
    max_riser, stair_width = res
    #max_riser = rs.RealBox(message = "Max riser height number", default_number = 170, title = "EnneadTab")
    max_riser, stair_width = float(max_riser), float(stair_width)
    DATA_FILE.set_sticky_longterm("MAX_RISER", max_riser)
    DATA_FILE.set_sticky_longterm("STAIR_RISER", stair_width)


    get_pt_instance = Rhino.Input.Custom.GetPoint()
    get_pt_instance.SetCommandPrompt("Stair Start Pt")
    get_pt_instance.Get()
    if get_pt_instance.CommandResult() != Rhino.Commands.Result.Success:
        return get_pt_instance.CommandResult()
    start_pt = get_pt_instance.Point()
    if start_pt == Rhino.Geometry.Point3d.Unset:
        return Rhino.Result.Failure

    get_dot_pt_instance = GetDotPoint(start_pt, max_riser, stair_width)
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


    get_flip_pt_instance = GetFlipPoint(start_pt, end_pt, max_riser, stair_width)
    get_flip_pt_instance.SetCommandPrompt("Stair End Pt")
    get_flip_pt_instance.ConstrainToConstructionPlane(False)
    get_flip_pt_instance.SetBasePoint(start_pt, True)
    get_flip_pt_instance.DrawLineFromPoint(start_pt, True)
    get_flip_pt_instance.Get()
    if get_flip_pt_instance.CommandResult() != Rhino.Commands.Result.Success:
        return get_flip_pt_instance.CommandResult()
    flip_pt = get_flip_pt_instance.Point()
    if flip_pt == Rhino.Geometry.Point3d.Unset:
        return Rhino.Result.Failure



    create_stair_block_from_pts(start_pt, end_pt, max_riser, stair_width, flip_pt )
    return
    radius = start_pt.DistanceTo(get_dot_pt_instance.Point())
    cplane = sc.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
    sc.doc.Objects.AddCircle(Rhino.Geometry.Circle(cplane, center_point, radius))
    sc.doc.Views.Redraw()
    return Rhino.Commands.Result.Success



class GetDotPoint (Rhino.Input.Custom.GetPoint):
    """Stemp 1"""
    def __init__(self, start_pt, max_riser, stair_width):
        self.start_pt = start_pt
        self.max_riser = max_riser
        self.stair_width = stair_width
        self.default_color = rs.CreateColor([87, 85, 83])
        #self.viewport = sc.doc.Views.ActiveView.ActiveViewport
    #


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
            mass_brep, note = make_stair_mass_brep(e, self.start_pt, end_pt, self.max_riser, self.stair_width)
            if mass_brep:
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

        e.Display.DrawDot  (self.start_pt, "Start Pt")



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




class GetFlipPoint (Rhino.Input.Custom.GetPoint):
    """Step 2"""

    def __init__(self, start_pt, end_pt, max_riser, stair_width):
        self.start_pt = start_pt
        self.end_pt = end_pt
        self.max_riser = max_riser
        self.stair_width = stair_width
        self.default_color = rs.CreateColor([87, 85, 83])
    #


    def show_text_with_pointer(self, e, text, size, color = None, is_middle_justified = False):
        if not color:
            color = self.default_color
        e.Display.Draw2dText(text, color, self.pointer_2d, is_middle_justified, size)
        #self.pointer_2d = Rhino.Geometry.Point2d(self.pointer_2d[0], self.pointer_2d[0] + size - 5)
        self.pointer_2d += Rhino.Geometry.Vector2d(0, size )


    def OnDynamicDraw(self, e):
        current_pt = e.CurrentPoint

        try:
            mass_brep, note = make_stair_mass_brep(e, self.start_pt, self.end_pt, self.max_riser, self.stair_width, current_pt)
            if mass_brep:
                e.Display.DrawBrepWires  (mass_brep, System.Drawing.Color.White, -1)
                e.Display.DrawBrepShaded (mass_brep, Rhino.Display.DisplayMaterial(System.Drawing.Color.Orange, 0))
        except:
            print (traceback.format_exc())
        e.Display.DrawDot  (self.start_pt, "Start Pt")
        e.Display.DrawDot  (self.end_pt, "End Pt")
        e.Display.DrawDot  (current_pt, "Pick Side")


        position_X_offset = 20
        position_Y_offset = 40
        bounds = e.Viewport.Bounds
        self.pointer_2d = Rhino.Geometry.Point2d(bounds.Left + position_X_offset, bounds.Top + position_Y_offset)
        title = "EnneadTab Stair Maker Mode"
        self.show_text_with_pointer(e,
                                    text = title,
                                    size = 30)
        self.show_text_with_pointer(e,
                                    text = "Pick A Side With Your Mouse, Click to Confirm",
                                    size = 30)
        self.show_text_with_pointer(e,
                                    text = note,
                                    size = 15)



if __name__ == "__main__":
    stair_maker()