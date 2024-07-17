
__title__ = "SampleLayout"
__doc__ = "Create sample block layout along crvs to quickly visualize design."
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import Rhino # pyright: ignore
import Eto # pyright: ignore


from EnneadTab import DATA_FILE, NOTIFICATION, SOUND, LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_UI, RHINO_OBJ_DATA


FORM_KEY = 'SAMPLE_BLOCK_modeless_form'




# make modal dialog
class SampleBlockDialog(Eto.Forms.Form):
    # Initializer
    def __init__(self):
        # Eto initials
        self.Title = "Sample Block Maker"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = 400
        self.width = 400
        self.selected_crvs = None
        self.user_block = None
        self.is_flipped = False
        self.Closed += self.OnFormClosed




        # initialize layout
        main_layout = Eto.Forms.DynamicLayout()
        main_layout.Padding = Eto.Drawing.Padding(5)
        main_layout.Spacing = Eto.Drawing.Size(5, 5)



        # add listBox
        main_layout.BeginVertical()
        main_layout.AddRow(self.CreatePicker())
        main_layout.AddRow(self.Create_block_info_inputs())
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
        self.InitiateFiller()
        
        RHINO_UI.apply_dark_style(self)

    @property
    def main_crv_geo(self):
        if self.selected_crvs:
            return [rs.coercecurve (x) for x in self.selected_crvs]
        return None

    @property
    def is_post_like(self):
        return self.mode_list.SelectedValue == self.mode_list.DataStore[1]

    """
    @property
    def is_flip_crv(self):
        # return check box isChecked
        return False
    """


    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        self.FOLDER_PRIMARY = r"L:\4b_Applied Computing\00_Asset Library"
        self.FOLDER_APP_IMAGES = r"{}\Database\app images".format(self.FOLDER_PRIMARY)
        self.LOGO_IMAGE = r"{}\Ennead_Architects_Logo.png".format(self.FOLDER_APP_IMAGES)
        temp_bitmap = Eto.Drawing.Bitmap(self.LOGO_IMAGE)
        self.logo.Image = temp_bitmap.WithSize(200,30)
        return self.logo

    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = "Pick an open/closed curve and preview its blocks fit thru them as panel or post."
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
        msg = Eto.Forms.Label()
        msg.Text = "Step 1:"
        layout.AddRow(msg)
        A = Eto.Forms.Label(Text = 'Pick closed or open crvs.\nMultiple input crvs now supported!\nThe flip the crv for dirent orientation.')
        layout.AddRow(A)

        pick_bn = Eto.Forms.Button(Text = 'Pick Input Curve(s).')
        pick_bn.Click += self.btn_Pick_Crv_Clicked

        self.crv_label = Eto.Forms.Label(Text = '')
        layout.AddRow(pick_bn,  None)
        layout.AddRow(self.crv_label)
        layout.AddRow(Rhino.UI.Controls.Divider())

        return layout

    def Create_block_info_inputs(self):


        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        stack_layout = Eto.Forms.DynamicLayout()
        stack_layout.Padding = Eto.Drawing.Padding(5)
        stack_layout.Spacing = Eto.Drawing.Size(5, 5)


        msg = Eto.Forms.Label()
        msg.Text = "Step 2:"
        layout.AddRow(msg)

        A = Eto.Forms.Label(Text = 'Panel mode spans block between divider pts.\nPost mode orient to local coordinate of the divider pts.')
        stack_layout.AddRow(A)
        self.mode_list = Eto.Forms.RadioButtonList()
        self.mode_list.Orientation = Eto.Forms.Orientation.Vertical
        self.mode_list.DataStore  = ["Panel mode", "Post mode"]
        self.mode_list.SelectedValue = self.mode_list.DataStore[0]
        self.mode_list.SelectedValueChanged += self.UI_changed
        stack_layout.AddRow(self.mode_list)
        layout.AddRow(stack_layout)


        layout.AddRow(Rhino.UI.Controls.Divider())
        msg = Eto.Forms.Label()
        msg.Text = "Step 3:"
        layout.AddRow(msg)

        stack_layout = Eto.Forms.DynamicLayout()
        stack_layout.Padding = Eto.Drawing.Padding(5)
        stack_layout.Spacing = Eto.Drawing.Size(5, 5)
        A = Eto.Forms.Label(Text = 'You can use your own block or use placeholder block.')
        stack_layout.AddRow(A)
        pick_bn = Eto.Forms.Button(Text = 'Pick Your Own Block')
        pick_bn.Click += self.btn_Pick_User_Block_Clicked
        clear_pick_bn = Eto.Forms.Button(Text = 'Clear User Block')
        clear_pick_bn.Click += self.btn_Clear_Pick_User_Block_Clicked
        stack_layout.AddRow(pick_bn, clear_pick_bn)
        self.user_block_label = Eto.Forms.Label(Text = ' ')
        stack_layout.AddRow(self.user_block_label)
        layout.AddRow(stack_layout)


        layout.AddRow(Rhino.UI.Controls.Divider())

        msg = Eto.Forms.Label()
        msg.Text = "Step 4:"
        layout.AddRow(msg)
        stack_layout = Eto.Forms.DynamicLayout()
        stack_layout.Padding = Eto.Drawing.Padding(5)
        stack_layout.Spacing = Eto.Drawing.Size(5, 5)
        A = Eto.Forms.Label(Text = 'Block spacing info in model unit:')

        stack_layout.AddRow( A)


        label = Eto.Forms.Label(Text = 'Using Smaller Text?')
        self.cbox_small_text = Eto.Forms.CheckBox()
        self.cbox_small_text.CheckedChanged += self.btn_preview_Clicked
        stack_layout.AddRow(label,  self.cbox_small_text)
        
        self.label_A = Eto.Forms.Label(Text = 'Panel Width')
        self.tbox_width = Eto.Forms.TextBox()
        stack_layout.AddRow(self.label_A,  self.tbox_width)

        self.label_B = Eto.Forms.Label(Text = 'Panel Height')
        self.tbox_height = Eto.Forms.TextBox()
        stack_layout.AddRow(self.label_B, self.tbox_height)

        self.label_C = Eto.Forms.Label(Text = 'Panel Depth')
        self.tbox_depth = Eto.Forms.TextBox()
        stack_layout.AddRow(self.label_C, self.tbox_depth)

        self.debug_label = Eto.Forms.Label(Text = 'Info:')
        stack_layout.AddRow(None, self.debug_label)

        layout.AddRow(stack_layout)


        return layout


    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []

        btn = Eto.Forms.Button()
        btn.Text = "Flip Orientation"
        btn.Click += self.btn_flip_orientation_Clicked
        user_buttons.append(btn)


        user_buttons.append(None)

        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Height = 30
        self.btn_Run.Text = "Update Preview"
        temp_bitmap = Eto.Drawing.Bitmap(r"{}\update_data.png".format(self.FOLDER_APP_IMAGES))
        #self.btn_Run.Image = temp_bitmap.WithSize(200,50)
        #self.btn_Run.Image = temp_bitmap
        self.btn_Run.ImagePosition = Eto.Forms.ButtonImagePosition.Right
        self.btn_Run.Click += self.btn_preview_Clicked
        user_buttons.append(self.btn_Run)



        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = "Add previewed block to file."
        self.btn_Run.Click += self.btn_process_Clicked
        user_buttons.append(self.btn_Run)

        #self.width = 400

        return user_buttons

    # event handler handling clicking on the 'run' button
    def UI_changed(self, sender, e):
        self.generate_blocks_layout(is_preview = True)
        if self.is_post_like:
            self.label_A.Text =  'Post Spacing'
            self.label_B.Text =  'Post Height'
            self.label_C.Text =  'Post Depth'
        else:
            self.label_A.Text =  'Panel Width'
            self.label_B.Text =  'Panel Height'
            self.label_C.Text =  'Panel Depth'

    # event handler handling clicking on the 'run' button
    def btn_preview_Clicked(self, sender, e):
        self.generate_blocks_layout(is_preview = True)


    def btn_process_Clicked(self, sender, e):
        self.generate_blocks_layout(is_preview = False)
        self.clear_out()
        

    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close()


    def btn_Pick_Crv_Clicked(self, sender, e):
        select_objs = rs.GetObjects(message = "Pick open or closed crvs.", filter = 4, select = True)
        if select_objs:
            temp_note = "{} base curve{} captured!".format(len(select_objs), "s" if len(select_objs) > 1 else "")
            self.crv_label.Text = temp_note
            NOTIFICATION.messenger(main_text = temp_note)
            map(rs.SimplifyCurve,select_objs)
            self.selected_crvs = select_objs
        else:
            temp_note = "Base curve not defined!"
            self.crv_label.Text = temp_note
            NOTIFICATION.messenger(main_text = temp_note)

        self.generate_blocks_layout(is_preview = True)



    def btn_Pick_User_Block_Clicked(self, sender, e):
        select_obj = rs.GetObject(message = "Pick a block you want to use in this sample layout.", filter = 4096, select = True)
        if select_obj:
            try:
                b_name = rs.BlockInstanceName(select_obj)
                self.user_block_label.Text = "User Block captured! <{}>".format(rs.BlockInstanceName(select_obj))
                self.user_block = select_obj
            except:
                temp_note = "This block is not from current file\nmight be from worksession file?"
                NOTIFICATION.messenger(main_text = temp_note)
                self.user_block = None
        else:
            self.user_block_label.Text = "User Block not defined! Will use sample block."
            self.user_block = None

        self.generate_blocks_layout(is_preview = True)



    def btn_Clear_Pick_User_Block_Clicked(self, sender, e):

        self.user_block_label.Text = "User Block not defined! Will use sample block."
        self.user_block = None

        self.generate_blocks_layout(is_preview = True)



    def btn_flip_orientation_Clicked(self, sender, e):

        self.is_flipped = not(self.is_flipped)
        if self.selected_crvs:
            map(rs.ReverseCurve, self.selected_crvs)
        self.generate_blocks_layout(is_preview = True)




    def generate_blocks_layout(self, is_preview):


        try:

            self.width = float(self.tbox_width.Text)
            self.height = float(self.tbox_height.Text)
            self.depth = float(self.tbox_depth.Text)
        except:
            print ("size data not valid")
            return


        if self.width * self.depth * self.height == 0:
            temp_note =  "size data not valid"
            NOTIFICATION.messenger(main_text = temp_note)
            return


        if not self.selected_crvs:
            temp_note =  "input crvs not is empty"
            NOTIFICATION.messenger(main_text = temp_note)
            return

        rs.UnselectAllObjects()
        rs.EnableRedraw(False)


        # need to remove preview crvs no matter what
        self.obj_name = "EA_BLOCK_LAYOUT_PREVIEW"
        old_crvs = rs.ObjectsByName(self.obj_name)
        rs.DeleteObjects(old_crvs)

        if not is_preview:
            self.obj_name = "EA_BLOCK_LAYOUT"
            SOUND.play_sound("sound effect_popup msg3.wav")
        else:
            SOUND.play_sound("sound effect_menu_tap.wav")
            


        # get block name if using user block

        # create sampleblock to get insert_pt and ref_pt
        block_name = "EA_layout block_{} x {} x {}".format(self.width, self.depth, self.height)
        block_name = make_unique_block_name(block_name)
        if self.is_post_like:
            block_name, insert_pt, ref_pt = self.create_post_block(block_name)
        else:
            block_name, insert_pt, ref_pt = self.create_panel_block(block_name)

        #  make temp block, use user block name or sampleblock
        if self.user_block:
            try:
                block_name = rs.BlockInstanceName(self.user_block)
            except:
                NOTIFICATION.messenger(main_text = "Invalid User Block...")
        self.temp_block = rs.InsertBlock(block_name, insert_pt)
        directional_ref = [0,1,0]
        self.block_reference = [insert_pt, ref_pt, directional_ref]

        #  flip crv if needed
        # if self.is_flipped:
        #     rs.ReverseCurve(self.selected_crvs)

        self.total_panel = 0
            

        map(self.process_base_crv, self.selected_crvs)
        rs.DeleteObject(self.temp_block)
        
        
        rs.Redraw()
        rs.EnableRedraw(True)
        if not is_preview:
            NOTIFICATION.messenger(main_text = "Blocks added!")

        self.debug_label.Text = "Panel Count = {}".format(self.total_panel)
        
        
    def process_base_crv(self, base_crv):
        # breakup base crv
        crv_segs = rs.ExplodeCurves(base_crv)

        #temporartyly set project osnap on to prevent flipping on X axis base line
        #original_project_osnap_status = rs.ProjectOsnaps()
        #rs.ProjectOsnaps(enable = True)

        collection = []
        #print crv_segs
        for seg in crv_segs:
            #print (rs.CurveLength(seg), self.width)

            count = round(rs.CurveLength(seg) / self.width)
            if count > 500:
                NOTIFICATION.messenger(main_text = "Too many segments for this block size...\nAre you sure the division width is in correct unit?")
                rs.DeleteObjects(crv_segs)
                break

            # divide the curve into segments of equal length
            pts_on_seg = rs.DivideCurve(seg, count, create_points = False)
            if not pts_on_seg:
                continue
            if rs.IsCurveClosed(seg):
                pts_on_seg.append(pts_on_seg[0])


            # if post mode and open crv then use all pts
            special_case = self.is_post_like and not rs.IsCurveClosed(base_crv)
            #special_case = 0
            for i in range(len(pts_on_seg) - 1 + special_case):
                x0 = pts_on_seg[i]
                #print x0
                if not self.is_post_like:
                    x1 = pts_on_seg[i + 1]
                param = rs.CurveClosestPoint(seg, x0)
                tangent = rs.CurveTangent(seg, param)

                side_vector = rs.VectorRotate(tangent, 90, [0,0,1])

                directional_ref_temp = x0 + side_vector

                if self.is_post_like:
                    target_reference = [x0, x0 + tangent, directional_ref_temp]
                    temp_placed_block = rs.OrientObject( self.temp_block, self.block_reference, target_reference, flags = 1 )


                else:
                    target_reference = [x0, x1, directional_ref_temp]
                    temp_placed_block = rs.OrientObject( self.temp_block, self.block_reference, target_reference, flags = 1 + 2)
                    if not temp_placed_block:
                        continue
                    scale_factor = rs.Distance(x0, x1)/self.width

                    local_plane = Rhino.Geometry.Plane(x0, x1, directional_ref_temp)
                    transform = Rhino.Geometry.Transform.Scale(local_plane, scale_factor, 1,1)

                    rs.TransformObject( temp_placed_block, transform, copy = False)


                collection.append(temp_placed_block)


            rs.DeleteObject(seg)


        
        rs.AddObjectsToGroup(collection, rs.AddGroup())
        map(lambda x: rs.ObjectName(x, self.obj_name), collection)
        

        self.total_panel += len(collection)


    def get_dot(self, text, box):
        height = 0.5
        if self.cbox_small_text.Checked:
            height = 0.02
        return rs.AddText(text,
                            RHINO_OBJ_DATA.get_center(box),
                            height = height,
                            font = "Arial",
                            font_style = 0,
                            justification = 2 + 131072 )
        
        
    def create_post_block(self, name):
        W, H, D = self.width/10, self.height, self.depth
        pt0 = [0,0,0]
        pt2 = [-W/2,0,0]
        pt1 = [W/2, W, H]
        pts = [pt1, pt2]
        ref_pt_coord = [W/2 , 0, 0]

        box_corners = rs.BoundingBox(pts)
        box = rs.AddBox(box_corners)
        dot = self.get_dot("Sample Post\n<{}>\nReplace block with better design.".format(name),box)

        insert_pt = rs.AddPoint(pt0)
        ref_pt = rs.AddPoint(ref_pt_coord)
        ref_line_start_pt = pt0
        ref_line_end_pt = [0, -W, 0]

        ref_line = rs.AddLine(ref_line_start_pt, ref_line_end_pt)
        block_contents = [box, insert_pt, ref_pt, ref_line, dot]
        block_name = rs.AddBlock(block_contents, insert_pt, name = name, delete_input = True)
        return block_name, pt0, ref_pt_coord

    def create_panel_block(self, name):
        W, H, D = self.width, self.height, self.depth

        pt0 = [0,0,0]
        pt1 = [W, D, H]
        pts = [pt0, pt1]
        ref_pt_coord = [W, 0, 0]

        box_corners = rs.BoundingBox(pts)
        box = rs.AddBox(box_corners)
        dot = self.get_dot("Sample Panel\n<{}>\nReplace block with better design.".format(name),box)
        #dot = rs.AddTextDot("Sample Panel <{}>\nReplace Me".format(name), RHINO_OBJ_DATA.get_center(box))
        insert_pt = rs.AddPoint(pt0)
        ref_pt = rs.AddPoint(ref_pt_coord)

        # make center ref line
        ref_line_start_pt = [W/2, 0, 0]
        ref_line_end_pt = [W/2, -W, 0]
        ref_line = rs.AddLine(ref_line_start_pt, ref_line_end_pt)

        # make corner ref lines
        corner_ref_lines = []
        corner_pts = [[0,0,0],
               [W,0,0],
               [W,0,H],
               [0,0,H]]
        for corner_pt in corner_pts:

            corner_ref_line_end_pt = [corner_pt[0], corner_pt[1]-W/2, corner_pt[2]]
            corner_ref_lines.append(rs.AddLine(corner_pt, corner_ref_line_end_pt))
            

        block_contents = [box, insert_pt, ref_pt, ref_line, dot] + corner_ref_lines
        block_name = rs.AddBlock(block_contents, insert_pt, name = name, delete_input = True)
        return block_name, pt0, ref_pt_coord


    def OnFormClosed(self, sender, e):
        self.Close()



    def InitiateFiller(self):

        self.filler_list = ["tbox_width","tbox_height", "tbox_depth", "cbox_small_text"]
        for x in self.filler_list:
            sticky_key = FORM_KEY + x
            default = 0
            value = DATA_FILE.get_sticky(sticky_key, default_value_if_no_sticky = default)


            box = getattr(self, x)
            if "tbox" in x:
                box.Text  = str(value)
            else:
                box.Checked = value


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

        for x in self.filler_list:
            if not hasattr(self, x):
                continue
            box = getattr(self, x)
            sticky_key = FORM_KEY + x
            #print x
            if "tbox" in x:
                DATA_FILE.set_sticky(sticky_key, box.Text)
            else:
                DATA_FILE.set_sticky(sticky_key, box.Checked)

        self.clear_out()



    def clear_out(self):
        obj_name = "EA_BLOCK_LAYOUT_PREVIEW"
        old_crvs = rs.ObjectsByName(obj_name)
        rs.DeleteObjects(old_crvs)
        for name in rs.BlockNames():
            if not name:
                continue
            if "EA_layout block_" in name and not rs.IsBlockInUse(name):
                rs.DeleteBlock(name)

        self.selected_crvs = None
        self.crv_label.Text = "Base curve empty."


def make_unique_block_name(block_name):
    while True:
        if block_name not in rs.BlockNames():
            break

        block_name += "_new"

    return block_name


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def sample_layout():
    rs.EnableRedraw(False)
    if sc.sticky.has_key(FORM_KEY):
        return
    dlg = SampleBlockDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    dlg.Show()
    sc.sticky[FORM_KEY] = dlg
    
if __name__ == "__main__":
    sample_layout()
