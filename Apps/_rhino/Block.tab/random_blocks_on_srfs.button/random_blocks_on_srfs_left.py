
__title__ = "RandomBlocksOnSrfs"
__doc__ = "Randomly create blocks on mutiple srfs, away from edge, along edge, or evenly on edge. It also allow pick guiding crv(s) or use edge as guides."
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import random
import Eto # pyright: ignore


from EnneadTab import DATA_FILE, NOTIFICATION, SOUND, TIME, LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_UI, RHINO_FORMS

FORM_KEY = 'SCATTER_BLOCK_ON_SRF_modeless_form'





# make modal dialog
class ScatterBlockDialog(Eto.Forms.Form):
    # Initializer
    def __init__(self):
        # Eto initials
        self.Title = "Scatter Blocks on Srf"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.Width = 600
        self.selected_srf = None
        self.selected_srfs = None
        self.user_blocks = None
        self.guide_crv = None
        self.internal_rotate_angle = 0
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
        last_layout = Eto.Forms.DynamicLayout()
        last_layout.Padding = Eto.Drawing.Padding(5)
        last_layout.Spacing = Eto.Drawing.Size(5, 5)
        layout.BeginVertical()
        last_layout.AddRow(*self.CreateButtons())
        layout.AddRow(last_layout)
        layout.EndVertical()

        # set content
        self.Content = layout
        self.InitiateFiller()
        
        RHINO_UI.apply_dark_style(self)




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
        self.msg.Text = "Pick surface(s) and sample blocks, then scatter blocks over surface with placement rules."
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
        
        stack_layout = Eto.Forms.DynamicLayout()
        stack_layout.Padding = Eto.Drawing.Padding(5)
        stack_layout.Spacing = Eto.Drawing.Size(5, 5)
        A = Eto.Forms.Label(Text = 'Pick surface(s).')
        stack_layout.AddRow(A)

        pick_bn = Eto.Forms.Button(Text = 'Pick Base Surface(s).')
        pick_bn.Click += self.btn_Pick_Srf_Clicked

        self.srf_label = Eto.Forms.Label(Text = '')
        stack_layout.AddRow(pick_bn,  None)
        stack_layout.AddRow(self.srf_label)
        layout.AddRow(stack_layout)
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

        A = Eto.Forms.Label(Text = 'Pick where blocks are placed.')
        stack_layout.AddRow(A)
        self.mode_list = Eto.Forms.RadioButtonList()
        self.mode_list.Orientation = Eto.Forms.Orientation.Vertical
        self.mode_list.DataStore  = ["Along Border Mode", "Avoid Border Mode", "Ignore Border Mode"]
        self.mode_list.SelectedValue = self.mode_list.DataStore[-1]
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
        A = Eto.Forms.Label(Text = 'Define which blocks you want to use.')
        stack_layout.AddRow(A)
        pick_bn = Eto.Forms.Button(Text = 'Pick Blocks')
        pick_bn.Click += self.btn_pick_block_clicked
        clear_pick_bn = Eto.Forms.Button(Text = 'Clear Blocks')
        clear_pick_bn.Click += self.btn_clear_blocks_clicked
        stack_layout.AddSeparateRow(pick_bn, None, clear_pick_bn)
        self.user_block_label = Eto.Forms.Label(Text = '\n\n\n')
        stack_layout.AddRow(self.user_block_label)
        layout.AddRow(stack_layout)


        layout.AddRow(Rhino.UI.Controls.Divider())

        msg = Eto.Forms.Label()
        msg.Text = "Step 4:"
        layout.AddRow(msg)
        stack_layout = Eto.Forms.DynamicLayout()
        stack_layout.Padding = Eto.Drawing.Padding(5)
        stack_layout.Spacing = Eto.Drawing.Size(5, 5)
        A = Eto.Forms.Label(Text = 'Block spacing info in model unit (per input surface):')

        stack_layout.AddRow( A)

        inner_stack_layout = Eto.Forms.DynamicLayout()
        inner_stack_layout.Padding = Eto.Drawing.Padding(5)
        inner_stack_layout.Spacing = Eto.Drawing.Size(5, 5)
        self.label_C = Eto.Forms.Label(Text = 'Desired Total Number')
        self.tbox_total_count = Eto.Forms.TextBox()
        inner_stack_layout.AddRow(self.label_C, self.tbox_total_count)

        self.label_A = Eto.Forms.Label(Text = 'Distance To Border')
        self.tbox_dist_to_border = Eto.Forms.TextBox()
        inner_stack_layout.AddRow(self.label_A,  self.tbox_dist_to_border)

        self.label_B = Eto.Forms.Label(Text = 'Minimal Distance Among Blocks\n(use -1 to ignore social distance)')
        self.tbox_minimal_internal_dist = Eto.Forms.TextBox()
        inner_stack_layout.AddRow(self.label_B, self.tbox_minimal_internal_dist)

        self.debug_label = Eto.Forms.Label(Text = 'Info:')
        inner_stack_layout.AddRow(None, self.debug_label)

        stack_layout.AddRow(inner_stack_layout)

        layout.AddRow(stack_layout)


        layout.AddRow(Rhino.UI.Controls.Divider())
        msg = Eto.Forms.Label()
        msg.Text = "Step 5:"
        layout.AddRow(msg)
        stack_layout = Eto.Forms.DynamicLayout()
        stack_layout.Padding = Eto.Drawing.Padding(5)
        stack_layout.Spacing = Eto.Drawing.Size(5, 5)
        A = Eto.Forms.Label(Text = 'Scater Mode:')
        stack_layout.AddRow( A)
        self.scatter_mode_list = Eto.Forms.RadioButtonList()
        self.scatter_mode_list.Orientation = Eto.Forms.Orientation.Vertical
        self.scatter_mode_list.DataStore  = ["Random", "Follow Guide Crv", "Follow Surface Edge"]
        self.scatter_mode_list.SelectedValue = self.scatter_mode_list.DataStore[0]
        self.scatter_mode_list.SelectedValueChanged += self.UI_changed
        stack_layout.AddRow(self.scatter_mode_list)


        self.pick_guide_crv_bn = Eto.Forms.Button(Text = 'Pick Guide Crv.')
        self.pick_guide_crv_bn.Click += self.btn_pick_guide_crv_clicked

        self.rotate_bn = Eto.Forms.Button(Text = 'Spin Block 90 degree.')
        self.rotate_bn.Click += self.btn_rotate_clicked

        self.guide_crv_label = Eto.Forms.Label(Text = '')
        stack_layout.AddSeparateRow(self.pick_guide_crv_bn, self.guide_crv_label, None, self.rotate_bn)
        layout.AddRow(stack_layout)
        
        self.pick_guide_crv_bn.Enabled = self.scatter_mode_list.SelectedValue == self.scatter_mode_list.DataStore[1]
        self.rotate_bn.Enabled = self.scatter_mode_list.SelectedValue != self.scatter_mode_list.DataStore[0]


        return layout


    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []



        user_buttons.append(None)

        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Height = 30
        self.btn_Run.Text = "(Re)Generate"
        temp_bitmap = Eto.Drawing.Bitmap(r"{}\update_data.png".format(self.FOLDER_APP_IMAGES))
        #self.btn_Run.Image = temp_bitmap.WithSize(200,50)
        #self.btn_Run.Image = temp_bitmap
        self.btn_Run.ImagePosition = Eto.Forms.ButtonImagePosition.Right
        self.btn_Run.Click += self.btn_preview_Clicked
        user_buttons.append(self.btn_Run)



        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = "Add Previewed Blocks To File."
        self.btn_Run.Height = 30
        self.btn_Run.Click += self.btn_process_Clicked
        user_buttons.append(self.btn_Run)

        #self.dist_to_border = 400

        return user_buttons


    def btn_rotate_clicked(self, sender, e):
        if not hasattr(self, "block_collection") or not self.block_collection: 
            NOTIFICATION.messenger(main_text = "No block defined.")
            return

        rs.EnableRedraw(False)

        z_vec = rs.VectorCreate([0,0,1], [0,0,0])


        SOUND.play_sound("sound effect_mario fireball.wav")
        for collection in self.total_collection:
            if collection is None: continue
            # print (collection)
            for block in collection:

                pt = rs.BlockInstanceInsertPoint(block)

                ang = 90
                rs.RotateObject(block, pt,ang,z_vec)
        rs.EnableRedraw(True)
    
        self.internal_rotate_angle += 90
        
    


    # event handler handling clicking on the 'run' button
    def UI_changed(self, sender, e):
        self.pick_guide_crv_bn.Enabled = self.scatter_mode_list.SelectedValue == self.scatter_mode_list.DataStore[1]
        self.rotate_bn.Enabled = self.scatter_mode_list.SelectedValue != self.scatter_mode_list.DataStore[0]
        
        
        if self.scatter_mode_list.SelectedValue == self.scatter_mode_list.DataStore[1]:
            pass

        self.generate_blocks_layout(is_preview = True)


    # event handler handling clicking on the 'run' button
    def btn_preview_Clicked(self, sender, e):
        self.generate_blocks_layout(is_preview = True)

    def btn_process_Clicked(self, sender, e):
        self.generate_blocks_layout(is_preview = False)
        self.clear_out()
        NOTIFICATION.messenger(main_text = "Blocks added")
        SOUND.play_sound("sound effect_popup msg1.wav")
        #self.Close()

    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close()


    def btn_Pick_Srf_Clicked(self, sender, e):
        select_objs = rs.GetObjects(message = "Pick Base Surfaces.", filter = rs.filter.surface, select = True)
        
        if select_objs:
            note = "Base surfaces captured!"
            self.srf_label.Text = note
            NOTIFICATION.messenger(main_text = note)
        
            self.selected_srfs = select_objs
        else:
            note = "Base surface not defined!"
            NOTIFICATION.messenger(main_text = note)
            SOUND.play_sound("sound effect_error.wav")
            
            self.srf_label.Text = note

        self.generate_blocks_layout(is_preview = True)


    def btn_pick_guide_crv_clicked(self, sender, e):
        select_obj = rs.GetObject(message = "Pick guide curve.", filter = rs.filter.curve, select = True)
        if select_obj:
            note = "  Guide curve captured!"
            self.guide_crv_label.Text = note
            NOTIFICATION.messenger(main_text = note)
        
            self.guide_crv = select_obj
        else:
            self.guide_crv_label.Text = "  Guide curve not defined!"
            SOUND.play_sound("sound effect_error.wav")

        self.generate_blocks_layout(is_preview = True)


    def btn_pick_block_clicked(self, sender, e):
        select_objs = rs.GetObjects(message = "Pick a block you want to use in this sample layout.", filter = 4096, select = True)
        if select_objs:
            block_names = list(set([rs.BlockInstanceName(x) for x in select_objs]))
            if len(block_names) > 1:
                
                block_names.sort()
                ratios = rs.PropertyListBox(block_names, [1] * len(block_names), message = "Ratio of each block type")
                ratios = [int(x) for x in ratios]
            else:
                ratios = [1]
            self.user_blocks = {name: ratio for name, ratio in zip(block_names, ratios)}

            names = ""
            for name, count in self.user_blocks.items():
                names += "<{}>={}  +  ".format(name, count)
            names = names.rstrip("  +  ")
            self.user_block_label.Text = "Blocks captured in following ratio!\n{}".format(names)
            
        else:
            self.user_block_label.Text = "User Block not defined! Please pick at least one block to scatter."
            self.user_block = None

        self.generate_blocks_layout(is_preview = True)



    def btn_clear_blocks_clicked(self, sender, e):

        self.user_block_label.Text = "User Block not defined! Please pick at least one block to scatter."
        self.user_blocks = None

        self.generate_blocks_layout(is_preview = True)



    @property
    def is_avoid_border(self):
        return self.mode_list.SelectedValue == self.mode_list.DataStore[1]

    @property
    def is_along_border(self):
        return self.mode_list.SelectedValue == self.mode_list.DataStore[0]

    @property
    def is_ignore_border(self):
        return self.mode_list.SelectedValue == self.mode_list.DataStore[-1]

    def delete_preview_blocks(self):
        obj_name = "EA_BLOCK_SCATTER_PREVIEW"
        old_blocks = rs.ObjectsByName(obj_name)
        rs.DeleteObjects(old_blocks)
        
        

    def generate_blocks_layout(self, is_preview):
        
   
        try:

            self.dist_to_border = float(self.tbox_dist_to_border.Text)
            self.minimal_internal_dist = float(self.tbox_minimal_internal_dist.Text)
            self.total_count = int(self.tbox_total_count.Text)
        except Exception as e:
            print (str(e))
            NOTIFICATION.messenger(main_text = "data not valid",
                                            print_note = True)
            SOUND.play_sound("sound effect_error.wav")
            self.delete_preview_blocks()
            return


        if self.total_count == 0:
            NOTIFICATION.messenger(main_text =  "Cannot have total count of 0 for scatter",
                                            print_note = True)
            SOUND.play_sound("sound effect_error.wav")
            
            self.delete_preview_blocks()
            return


        if not self.selected_srfs:
            NOTIFICATION.messenger(main_text = "Base srfs not valid",
                                            print_note = True)
            SOUND.play_sound("sound effect_error.wav")
            
            self.delete_preview_blocks()
            return
        

        if self.scatter_mode_list.SelectedValue == self.scatter_mode_list.DataStore[1]:
            if not self.guide_crv or not rs.IsObject(self.guide_crv):
                NOTIFICATION.messenger(main_text = "Guide curve not valid",
                                            print_note = True)
                SOUND.play_sound("sound effect_error.wav")
      
                self.delete_preview_blocks()
                return


        # if preview_mode, need to remove preview crvs no matter what
        if is_preview:
            self.obj_name = "EA_BLOCK_SCATTER_PREVIEW"
            old_blocks = rs.ObjectsByName(self.obj_name)
            rs.DeleteObjects(old_blocks)

        else: 
            # is not preview, then can exist
            self.obj_name = "EA_SCATTER_BLOCK"
            for collection in self.total_collection:
                map(lambda x: rs.ObjectName(x, self.obj_name), collection)
            return

        if not self.user_blocks:
            
            NOTIFICATION.messenger(main_text = "User block not valid")
            SOUND.play_sound("sound effect_error.wav")
            
            return
        rs.UnselectAllObjects()
        rs.EnableRedraw(False)
        

        self.total_collection = []
        for srf in self.selected_srfs:
            self.selected_srf = srf
            self.generate_blocks_layout_action(is_preview)
            self.total_collection.append(self.block_collection) 
            rs.Redraw()
        rs.EnableRedraw(True)
        


    def generate_blocks_layout_action(self, is_preview):


        # generate base pts
        domainU = rs.SurfaceDomain(self.selected_srf, 0)
        domainV = rs.SurfaceDomain(self.selected_srf, 1)
        self.borders = rs.DuplicateSurfaceBorder(self.selected_srf)
        # print domainU
        # print domainV
        domainU_diff = domainU[1] - domainU[0]
        domainV_diff = domainV[1] - domainV[0]


        """
        with some near threhold setting, it might be immposobile to find max count pts. So a timer is needed to stop loop since last pts add to list.
        """
        self.pt_collection = []
        success_time_mark = TIME.mark_time()
        count = 0
        while count < self.total_count:
            time_span = TIME.time_span(success_time_mark)
            # if count%20 == 0:
            #     sc.doc.Views.Redraw()
            #     Rhino.RhinoApp.Wait()


            if time_span > 1:


                RHINO_FORMS.notification(main_text = "Cannot add more blocks with current setting",
                                                        sub_text = "Maybe the min spacing is set too high for the given base srf size, or the target pts count is too much.\n\nFinal {} pts added".format(len(self.pt_collection)), 
                                                        self_destruct = 5,
                                                        button_name = "Sure...",
                                                        width = 400,
                                                        height = 300)
                break
            U = random.random() * domainU_diff + domainU[0]
            V = random.random() * domainV_diff + domainV[0]
            pt = rs.EvaluateSurface(self.selected_srf, U, V)

            if not rs.IsPointOnSurface(self.selected_srf, pt):
                continue


            if self.is_avoid_border and self.is_pt_close_to_border(pt):
                continue
            if self.is_along_border and not self.is_pt_close_to_border(pt):
                continue

            if self.is_pt_close_to_existing_pts(pt):
                continue

            #print pt
            self.pt_collection.append( pt )
            """
            add rhino progress bar here,
            add time stamp reset for the last susceeful appending of pt. If too long since last addition, there might be problem in the thresshold setting.
            """
            success_time_mark = TIME.mark_time()
            count += 1

        if is_preview:
            SOUND.play_sound("sound effect_popup msg2.wav")
        else:
            SOUND.play_sound("sound effect_popup msg1.wav")
        rs.DeleteObjects(self.borders)



        sample_list = []
        for name, count in self.user_blocks.items():
            sample_list.extend([name] * count)

        self.block_collection = []
        for pt in self.pt_collection:
            picked_block_name = random.choice(sample_list)
            scale = (1,1,random.uniform(0.9,1.1))
            if self.scatter_mode_list.SelectedValue == self.scatter_mode_list.DataStore[0] :
                rotation = random.random() * 360
            elif self.scatter_mode_list.SelectedValue == self.scatter_mode_list.DataStore[1] :
                rotation = self.get_rotation_from_guide_crv(pt)
                #print rotation
            else:
                borders = rs.DuplicateSurfaceBorder(self.selected_srf)
                self.srf_edge_crv  = borders[0]
                rotation = self.get_rotation_from_guide_crv(pt, use_edge = True)
                self.srf_edge_crv  = None
                rs.DeleteObjects(borders)
                
            rotation_normal = (0,0,1)
            block = rs.InsertBlock(picked_block_name, pt, scale, rotation, rotation_normal)
            self.block_collection.append(block)

        rs.AddObjectsToGroup(self.block_collection, rs.AddGroup())
        map(lambda x: rs.ObjectName(x, self.obj_name), self.block_collection)
        


       

        total_panel = len(self.total_collection)
        self.debug_label.Text = "Blocks Count = {}".format(total_panel)



    def get_rotation_from_guide_crv(self, pt, use_edge = False):

        if use_edge:
            rule_crv = self.srf_edge_crv
        else:
            rule_crv = self.guide_crv
            
        para = rs.CurveClosestPoint(rule_crv, pt)
        tangent = rs.CurveTangent(rule_crv, para)
      
        return -rs.VectorAngle(Rhino.Geometry.Vector3d (1,0,0), tangent) + self.internal_rotate_angle



    def is_pt_close_to_existing_pts(self, pt):
        if self.minimal_internal_dist < 0:
            return False
        if len(self.pt_collection) == 0:
            return False
        
        for other_pt in self.pt_collection:
            dist = pt.DistanceTo(other_pt)
            if dist < self.minimal_internal_dist:
                return True
        else:
            return False


        closest_pt = rs.PointClosestObject(pt, self.pt_collection)[1]
        dist = rs.Distance(pt, closest_pt)
        return dist < self.minimal_internal_dist

    def is_pt_close_to_border(self, pt):

        for border in self.borders:
            para = rs.CurveClosestPoint(border, pt)
            closest_pt = rs.EvaluateCurve(border, para)
            dist = rs.Distance(pt, closest_pt)

            if dist < self.dist_to_border: return True
        
        
        return False



    def OnFormClosed(self, sender, e):
        self.Close()



    def InitiateFiller(self):

        self.filler_list = ["tbox_dist_to_border","tbox_minimal_internal_dist", "tbox_total_count"]
        for x in self.filler_list:
            sticky_key = FORM_KEY + x
            default = 0
            value = DATA_FILE.get_sticky(sticky_key, default_value_if_no_sticky = default)

            #setattr(self, x , str(value))
            tbox = getattr(self, x)
            tbox.Text  = str(value)


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
            tbox = getattr(self, x)
            sticky_key = FORM_KEY + x
            #print x
            DATA_FILE.set_sticky(sticky_key, tbox.Text)

        self.clear_out()

    def clear_out(self):
        obj_name = "EA_BLOCK_SCATTER_PREVIEW"
        old_crvs = rs.ObjectsByName(obj_name)
        rs.DeleteObjects(old_crvs)


        self.selected_srf = None
        self.selected_srfs = None
        self.srf_label.Text = "Base srfs empty."




def random_blocks_on_srfs():
    rs.EnableRedraw(False)
    if sc.sticky.has_key(FORM_KEY):
        return
    dlg = ScatterBlockDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    dlg.Show()
    sc.sticky[FORM_KEY] = dlg

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def make_unique_block_name(block_name):
    
    while True:
        if block_name not in rs.BlockNames():
            break

        block_name += "_new"

    return block_name


if __name__ == "__main__":
    random_blocks_on_srfs()