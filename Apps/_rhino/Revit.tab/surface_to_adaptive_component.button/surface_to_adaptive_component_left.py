
__title__ = "SurfaceToAdaptiveComponent"
__doc__ = "Use the corners of the input surfs as the marker for the adaptive pts in Revit."

import Eto # pyright: ignore
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab import DATA_FILE, FOLDER, SOUND
from EnneadTab.RHINO import RHINO_UI, RHINO_OBJ_DATA

FORM_KEY = 'srf2adp_modeless_form'



# make modal dialog
class Srf2AdpDialog(Eto.Forms.Form):
    # Initializer
    def __init__(self):
        # Eto initials
        self.Title = "Srf2Adp Data transfer"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        
        self.height = 400
        self.width = 400
        self.selected_srfs = None
        self.order = 0
        self.is_reversed = False
        self.out_data = None


        self.Closed += self.OnFormClosed




        # initialize layout
        main_layout = Eto.Forms.DynamicLayout()
        main_layout.Padding = Eto.Drawing.Padding(5)
        main_layout.Spacing = Eto.Drawing.Size(5, 5)



        # add listBox
        main_layout.BeginVertical()
        main_layout.AddRow(self.CreatePicker())
        main_layout.AddRow(self.CreateOrderControl())
        main_layout.EndVertical()





        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        # add message
        layout.AddSeparateRow(None, self.CreateLogoImage())
        layout.BeginVertical()
        layout.AddRow(self.CreateMessageBar())
        layout.AddRow(self.CreateExpander())
        layout.EndVertical()


        layout.BeginVertical()
        layout.AddRow(main_layout)
        layout.EndVertical()

        # add buttons
        layout.BeginVertical()
        layout.AddRow(*self.CreateButtons())
        layout.EndVertical()

        # set content
        self.Content = layout
        
        
        RHINO_UI.apply_dark_style(self)
        


    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        return self.logo

    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = "Pick surfaces/polysurfaceswhose corners represent adaptive family corners."
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left


    def CreateExpander(self):
        self.expander = Eto.Forms.Expander ()
        self.expander.Header = "Quick Help"
        self.expander.Expanded = False
        msg = Eto.Forms.Label()
        msg.Text = "helper document to be filled in....."
        self.expander.Content = msg
        return self.expander



    def CreatePicker(self):
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        A = Eto.Forms.Label(Text = 'Pick surfaces/plysurface. The corner order will the sequence adaptive family is hosting points.\nEither from manual definition or Grasshopper Lunchbox bake.')
        layout.AddRow(A)

        pick_bn = Eto.Forms.Button(Text = 'Pick Input Surfaces.')
        pick_bn.Click += self.btn_Pick_Srf_Clicked

        self.srf_label = Eto.Forms.Label(Text = '')
        layout.AddRow(pick_bn,  None)
        layout.AddRow(self.srf_label)
        layout.AddRow(Rhino.UI.Controls.Divider())

        return layout

    def CreateOrderControl(self):


        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        stack_layout = Eto.Forms.DynamicLayout()
        stack_layout.Padding = Eto.Drawing.Padding(5)
        stack_layout.Spacing = Eto.Drawing.Size(5, 5)

        A = Eto.Forms.Label(Text = 'Rotate the order of the corner points.')
        stack_layout.AddSeparateRow(None,A, None)

        rotate_A_bn = Eto.Forms.Button(Text = '<')
        rotate_A_bn.Click += self.btn_rotate_A_Clicked
        reverse_bn = Eto.Forms.Button(Text = 'Flip Order')
        reverse_bn.Click += self.reverse_bn_Clicked
        rotate_B_bn = Eto.Forms.Button(Text = '>')
        rotate_B_bn.Click += self.btn_rotate_B_Clicked
        stack_layout.AddSeparateRow(None, rotate_A_bn, reverse_bn, rotate_B_bn, None)
        
        
        layout.AddRow(stack_layout)


        return layout


    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []

       
        user_buttons.append(None)




        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = "Accept this order."
        self.btn_Run.Click += self.btn_process_Clicked
        user_buttons.append(self.btn_Run)

        #self.width = 400

        return user_buttons

    # event handler handling clicking on the 'run' button
    def UI_changed(self, sender, e):
        pass

    def btn_process_Clicked(self, sender, e):
        if not self.out_data:
            return
            
        file = FOLDER.get_EA_dump_folder_file("SRF2ADP_DATA.sexyDuck")
        DATA_FILE.set_data(self.out_data, file)

        SOUND.play_sound("sound_effect_mario_message.wav")
        self.clear_out()
        self.Close()

    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close()

    def btn_Pick_Srf_Clicked(self, sender, e):
        self.selected_srfs = rs.GetObjects("Select object to transfer data", filter = 8+16)
        
        if len(self.selected_srfs) > 0:
            #print self.selected_srfs
            self.srf_label.Text = "{} Surfaces selected.".format(len(self.selected_srfs))
            self.generate_dot_and_data()
        
    
        else:
            self.srf_label.Text = "Base surfaces not defined!"

    def reverse_bn_Clicked(self, sender, e):
        self.is_reversed = not self.is_reversed
        self.generate_dot_and_data()

    def btn_rotate_A_Clicked(self, sender, e):
        self.order += 1
        self.generate_dot_and_data()
    

    def btn_rotate_B_Clicked(self, sender, e):
        self.order -= 1
        self.generate_dot_and_data()

    def generate_dot_and_data(self):

        self.clear_out()
        if self.selected_srfs is None:
            return
        if len(self.selected_srfs) == 0:
            return
        rs.EnableRedraw(False)


        self.out_data = dict()
        max = len(self.selected_srfs)
        rs.StatusBarProgressMeterShow(label = "Total Srf to process <{}> ".format(max), lower = 0, upper = max, embed_label = True, show_percent = True)
        for i, srf in enumerate(self.selected_srfs):
            rs.StatusBarProgressMeterUpdate(position = i, absolute = True)
            data = self.process_srf(srf)
            if data:
                self.out_data[srf.ToString()] = data
        rs.StatusBarProgressMeterHide()
        rs.EnableRedraw(True)

    

    def OnFormClosed(self, sender, e):
        self.Close()



    def Close(self):
        # Remove the events added in the initializer
        #self.RemoveEvents()
        # Dispose of the form and remove it from the sticky dictionary
        if sc.sticky.has_key(FORM_KEY):
            form = sc.sticky[FORM_KEY]
            if form:
                form.Dispose()
                form = None
            sc.sticky.Remove(FORM_KEY)



        self.clear_out()

    def clear_out(self):
            
        old_dots = rs.ObjectsByName("SRF2ADP_DOTS")
        if old_dots:
            rs.DeleteObjects(old_dots)
   

        #self.selected_srfs = None
        #self.srf_label.Text = "Base surfaces not defined!"



    def process_srf(self, srf):
        # print brep
        brep = sc.doc.Objects.Find(srf).Geometry
        #print brep
        faces = brep.Faces
        #print brep.Edges
        out = dict()
        for i, face in enumerate(faces):
            #print face
            """

            edge_loop = face.OuterLoop
            edge_crv = edge_loop.To3dCurve()
            """
            """
            extrac_face = faces.ExtractFace(i)
            extrac_face.Vertices
            """
            temp_brep = face.DuplicateFace (False)
        

            tol = sc.doc.ModelAbsoluteTolerance
            ang_tol = sc.doc.ModelAngleToleranceRadians

            joined_crvs = Rhino.Geometry.Curve.JoinCurves( temp_brep.Edges, tol)
            
            ##### this skipp any hole it might have
            outter_crv = sorted(joined_crvs, key = lambda x: x.GetLength())[-1]



            pts = outter_crv.Simplify (Rhino.Geometry.CurveSimplifyOptions.All, tol, ang_tol).ToNurbsCurve ().GrevillePoints()

            #  get rid of the first point
            pts = list(pts)[1:]
            #print pts

            # shift pts in pts list by order
            local_order = self.order % len(pts)
            pts = pts[local_order:] + pts[:local_order]

            if self.is_reversed:
                pts.reverse()


            # pts = temp_brep.Vertices
            dots = []
            for j, pt in enumerate(pts):
    
                #print pt
                dots.append(rs.AddTextDot(str(j + 1),pt))
            
            factor = 0.8
            rs.ScaleObjects(dots, RHINO_OBJ_DATA.get_center(dots), [factor]*3)
            rs.ObjectName(dots, "SRF2ADP_DOTS")
            out[i] = [[x[0], x[1], x[2]] for x in pts]
            continue
        
        return out






@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def surface_to_adaptive_component():
    rs.EnableRedraw(False)
    if sc.sticky.has_key(FORM_KEY):
        return
    dlg = Srf2AdpDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    sc.sticky[FORM_KEY] = dlg
    dlg.Show()

if __name__ == "__main__":
    surface_to_adaptive_component()