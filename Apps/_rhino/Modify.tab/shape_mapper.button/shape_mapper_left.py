
__title__ = "ShapeMapper"
__doc__ = "This button does ShapeMapper when left click"
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import clr # pyright: ignore
import os

import imp
random_color_module = imp.load_source("random_layer_color", r'L:\\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Layers\random_layer_color.py')



import Eto # pyright: ignore

from EnneadTab.RHINO import RHINO_UI, RHINO_OBJ_DATA
from EnneadTab import NOTIFICATION, DATA_FILE, ERROR_HANDLE
FORM_KEY = 'shape_mapper_modeless_form'



class Morph_Solution:
    def __init__(self, srf, session_name, offset_data):
        
        self.input_srf = srf
        self.session_name = session_name
        self._design_ref_offset_x = offset_data[0]
        self._design_target_offset_x = offset_data[1]
        self._design_target_offset_z = offset_data[2]
        
        
        self._parent_layer = "EA_Facade Mapping_[{}]::".format(self.session_name)
        self._help_layers = ["design_geos",
                            "source_srf", 
                            "ref_srf", 
                            "#note: put crvs and srf in <design_geo> or the child layer of it.", 
                            "#note: source srf X+ {} of design line".format(self._design_ref_offset_x), 
                            "#note: ref srf X+ {} of target location".format(self._design_target_offset_x),
                            "#note: ref srf Z- {} of target location".format(self._design_target_offset_z)]
        if srf:
            rs.EnableRedraw(False)
            self.initiate_layers()
            self.make_drafting_area()
            rs.EnableRedraw(True)
        
    def initiate_layers(self):
 
        
        is_creating_layer_tree = False
        for x in self._help_layers:
            if not rs.IsLayer(self._parent_layer + x):
                rs.AddLayer(self._parent_layer + x)
                is_creating_layer_tree = True
                
        if is_creating_layer_tree:
            random_color_module.random_layer_color(default_opt = True)
            
            
    def make_drafting_area(self):
        copy = rs.CopyObject(self.input_srf, [self._design_target_offset_x, 
                                        0,
                                        -self._design_target_offset_z])
        rs.ObjectLayer(copy, self._parent_layer + self._help_layers[2])
        
        size_U = clr.StrongBox[float](0.0)
        size_V = clr.StrongBox[float](0.0)
        rs.coercesurface(self.input_srf).GetSurfaceSize(size_U, size_V)
        size_U = size_U.Value
        size_V = size_V.Value
        
        
        # size_U = rs.SurfaceDomain(raw_srf, 0)[1]-rs.SurfaceDomain(raw_srf, 0)[0]
        # size_V = rs.SurfaceDomain(raw_srf, 1)[1]-rs.SurfaceDomain(raw_srf, 1)[0]
        pts = [rs.AddPoint([0,0,0]),
                rs.AddPoint([size_U,0,0]),
                rs.AddPoint([size_U, size_V, 0]),
                rs.AddPoint([0, size_V, 0])]
        ref_srf = rs.AddSrfPt(pts)
        rs.DeleteObjects(pts)
        
        control_pt = RHINO_OBJ_DATA.get_obj_min_center_pt(copy)
        ref_srf = rs.MoveObject(ref_srf, [self._design_ref_offset_x + size_U, 
                                        0,
                                        -self._design_target_offset_z])
        ref_srf = rs.MoveObject(ref_srf, [control_pt[0],
                                        control_pt[1],
                                        0])
        rs.ObjectLayer(ref_srf, self._parent_layer + self._help_layers[1])
        
        border = rs.DuplicateSurfaceBorder(ref_srf)
        [rs.ObjectLayer(x, self._parent_layer + self._help_layers[3]) for x in border]
        rs.MoveObjects(border, [-self._design_ref_offset_x,
                                0,
                                0])
        dot = rs.AddTextDot("DELETE ME LATER:\nDraw your design crvs, srfs and polysrfs\nin this crv border use layer tree to organize the design.\nYou can relocate the border crv to any location but the\nsource srf MUST move along.(Keeping relative position)",
                        RHINO_OBJ_DATA.get_center(border[0]))
        rs.ObjectLayer(dot, self._parent_layer.split("::")[0])
                    



    
    def morph_along_srf(self):
        rs.EnableRedraw(False)
    
        if not self.prepare_morph_geo():
            return
    
    
        layers_to_process = [self._parent_layer + self._help_layers[0]]
        sub_layers =  rs.LayerChildren(layers_to_process[0])
        layers_to_process.extend(sub_layers)
        
        map(self.process_layer, layers_to_process)
        
        if hasattr(self, "_temp_source_srf"):
            rs.DeleteObject(self._temp_source_srf)
        NOTIFICATION.messenger(main_text= "Mapping Geos updated!")
        rs.EnableRedraw(True)
                

    def prepare_morph_geo(self):
        source_srf = rs.ObjectsByLayer(self._parent_layer + self._help_layers[1])
        if len( source_srf) != 1:
            NOTIFICATION.messenger(main_text= "1 and only 1 srf should be placed in layer <{}>".format(self._parent_layer + self._help_layers[1]))
            return False
        source_srf = source_srf[0]
        
        target_srf = rs.ObjectsByLayer(self._parent_layer + self._help_layers[2])
        if len( target_srf) != 1:
            NOTIFICATION.messenger(main_text= "1 and only 1 srf should be placed in layer <{}>".format(self._parent_layer + self._help_layers[2]))
    
            return False
        target_srf = target_srf[0]
        
        
        self._temp_source_srf = rs.CopyObject(source_srf, [-self._design_ref_offset_x,0,0])
        
        self._morph_obj = Rhino.Geometry.Morphs.SporphSpaceMorph (sc.doc.Objects.Find(self._temp_source_srf).Geometry.Surfaces[0], 
                                                        sc.doc.Objects.Find(target_srf).Geometry.Surfaces[0])
        return True
    
    
    def process_layer(self, layer):   
        # print "processing--->" + layer
        objs_to_map = rs.ObjectsByLayer(layer)
            
            
            
        if len( objs_to_map) == 0:
            NOTIFICATION.messenger(main_text= "There should be some geos in layer <{}>".format(layer))
            return
        
        crvs_to_map = [x for x in objs_to_map if rs.IsCurve(x)]
        srfs_to_map = [x for x in objs_to_map if rs.IsSurface(x)]
        polysrfs_to_map = [x for x in objs_to_map if rs.IsPolysurface(x)]
        
        # print crvs_to_map
        # print srfs_to_map
        # print polysrfs_to_map
        temp_copy_design_crvs = rs.CopyObjects(crvs_to_map)
        for crv in temp_copy_design_crvs:
            if rs.IsCircle(crv):
                NOTIFICATION.messenger(main_text="Circle crv is not my favorite...")
            if rs.CurveDegree(crv) == 1:
                rs.RebuildCurve(crv)
                
                
        if len(crvs_to_map) >= 2:
            temp_copy_design_crvs = rs.JoinCurves(temp_copy_design_crvs, delete_input=True)
            
        

        
        # pocess all the crv map
        abstract_crvs = [sc.doc.Objects.Find(x).Geometry for x in temp_copy_design_crvs]
        map(self._morph_obj.Morph,abstract_crvs)
        res_crv = [sc.doc.Objects.AddCurve(x) for x in abstract_crvs]

        # pocess all the srf map----:note: using same method as polysurface
        # abstract_srfs = [sc.doc.Objects.Find(x).Geometry for x in srfs_to_map]
        # map(self._morph_obj.Morph,abstract_srfs)
        # res_srf = [sc.doc.Objects.AddBrep(x) for x in abstract_srfs]

        # pocess all the polysrf map
        abstract_breps = []
        for x in srfs_to_map + polysrfs_to_map:
            if sc.doc.Objects.Find(x).ShortDescription(False) == "extrusion":
                abstract_brep = sc.doc.Objects.Find(x).Geometry.ToBrep()
            else:
                abstract_brep = sc.doc.Objects.Find(x).Geometry
            abstract_breps.append(abstract_brep)

        map(self._morph_obj.Morph,abstract_breps)
        res_brep = [sc.doc.Objects.AddBrep(x) for x in abstract_breps]
        
        res = res_crv +  res_brep
        
        # cleanup exsiting crv mapped
        for x in res:
            # layer = rs.ObjectLayer(x)

            new_layer = "Mapped_Facade_[{}]::".format(self.session_name) + layer.split("::")[-1]
            if rs.IsLayer(new_layer):
                rs.PurgeLayer(new_layer)
        
        # get them to a dececated layer parrent
        for x in res:
            # layer = rs.ObjectLayer(x)
            layer_color = rs.LayerColor(layer)
            layer_material = rs.LayerMaterialIndex(layer)
            new_layer = "Mapped_Facade_[{}]::".format(self.session_name) + layer.split("::")[-1]

            try:
                rs.AddLayer(new_layer)
                rs.LayerColor(new_layer, layer_color)
                rs.LayerMaterialIndex(new_layer, layer_material)
            except:
                pass
            rs.ObjectLayer(x, new_layer)
            
        # tidy up at end
        rs.AddObjectsToGroup(res, rs.AddGroup())
        rs.MoveObjects(res, [-self._design_target_offset_x,
                             0,
                             self._design_target_offset_z])
        rs.DeleteObjects(temp_copy_design_crvs)


# make modal dialog
class ShapeMapperDialog(Eto.Forms.Form):
    # Initializer
    def __init__(self):
        # Eto initials
        self.Title = "Shape Mapper"
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        
        self.height = 400
        self.width = 100
        
        self.Closed += self.OnFormClosed
        
        self.ui_input = ["tbox_session_name",
                         "tbox_design_ref_offset_x",
                         "tbox_design_target_offset_x",
                         "tbox_design_target_offset_z"]




        # initialize layout
        main_layout = Eto.Forms.DynamicLayout()
        main_layout.Padding = Eto.Drawing.Padding(5)
        main_layout.Spacing = Eto.Drawing.Size(5, 5)



       
        main_layout.BeginVertical()
        main_layout.AddRow(self.create_ui_new_source())
        main_layout.AddRow( Rhino.UI.Controls.Divider())
        main_layout.AddRow(self.create_ui_gap_input())
        main_layout.AddRow( Rhino.UI.Controls.Divider())
        main_layout.AddRow(self.create_ui_control())
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
        layout.AddRow(None, main_layout, None)
        layout.EndVertical()

        # add buttons
       
        layout.AddSeparateRow(*self.CreateButtons())
    

        # set content
        layout.Width = 400
        self.Content = layout
        self.InitiateFiller()
        
        # print self.Content
        RHINO_UI.apply_dark_style(self)

  


    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()
        return self.logo

    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = "Design on flat, map it anywhere."
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


    def create_ui_new_source(self):
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        
        A = Eto.Forms.Label(Text = 'Pick a new surface to initate a mapper.')
        layout.AddSeparateRow(A)
        
        self.tbox_session_name = Eto.Forms.TextBox()
        self.tbox_session_name.TextAlignment = Eto.Forms.TextAlignment.Center
        pick_bn = Eto.Forms.Button(Text = 'Pick Surface.')
        pick_bn.Click += self.btn_pick_new_srf
        
        layout.AddSeparateRow(Eto.Forms.Label(Text="Session Name: "), self.tbox_session_name,  pick_bn)


        self.srf_label = Eto.Forms.Label(Text = '')
 
        layout.AddSeparateRow(None, self.srf_label, None)
        
        return layout
        
        
        
    def create_ui_gap_input(self):
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        
        A = Eto.Forms.Label(Text = 'Offset gap between crv and flat srf: ')
  
        self.tbox_design_ref_offset_x = Eto.Forms.TextBox()
        self.tbox_design_ref_offset_x.Width = 100
        self.tbox_design_ref_offset_x.TextAlignment = Eto.Forms.TextAlignment.Center
        layout.AddRow(A, self.tbox_design_ref_offset_x)
        
        A = Eto.Forms.Label(Text = 'Offset gap for target srf X: ')

        self.tbox_design_target_offset_x = Eto.Forms.TextBox()
        self.tbox_design_target_offset_x.Width = 100
        self.tbox_design_target_offset_x.TextAlignment = Eto.Forms.TextAlignment.Center
        layout.AddRow(A, self.tbox_design_target_offset_x)
        
        
        A = Eto.Forms.Label(Text = 'Offset gap for target srf Z: ')
  
        self.tbox_design_target_offset_z = Eto.Forms.TextBox()
        self.tbox_design_target_offset_z.Width = 100
        self.tbox_design_target_offset_z.TextAlignment = Eto.Forms.TextAlignment.Center
        layout.AddRow(A, self.tbox_design_target_offset_z)

        return layout


    @ERROR_HANDLE.try_catch_error
    def create_ui_control(self):
        
        # control for hide unhide all tagger dot(will handle both user input and conduit dot)
        
        #control for pick color for a name
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        

        
        bt_zoom_design = Eto.Forms.Button()
        bt_zoom_design.Text = " Zoom Design Area "
        bt_zoom_design.Click += self.on_zoom_design_area_click
        bt_zoom_mapped = Eto.Forms.Button()
        bt_zoom_mapped.Text = " Zoom Mapped Area "
        bt_zoom_mapped.Click += self.on_zoom_mapped_area_click
        
        layout.AddSeparateRow(None, bt_zoom_design, bt_zoom_mapped, None)
        
        
        layout.AddRow(Rhino.UI.Controls.Divider())
        
        
        self.session_name_list = Eto.Forms.ListBox()
        self.session_name_list.Height = 150
        self.session_name_list.SelectedIndexChanged += self.on_selected_index_changed
        # self.session_name_list.MouseMove += self.on_selected_index_changed
        self.reset_listbox()
        layout.AddSeparateRow(Eto.Forms.Label(Text = "Existing mapper sessions\nin current document:\n\n(Double click to highlight design layer)",
                                              VerticalAlign=Eto.Forms.VerticalAlign.Top ),
                              None,
                              self.session_name_list)
        
       
        return layout

    def reset_listbox(self):
        self.session_name_list.Items.Clear()
        [self.session_name_list.Items.Add(x) for x in self.get_all_session_names()]
        
        
    # Listbox.SelectedIndexChanged event handler
    @ERROR_HANDLE.try_catch_error
    def on_selected_index_changed(self, sender, e):
        if not self.selected_session_name:
            return
        
        
        rs.EnableRedraw(False)
        rs.CurrentLayer("EA_Facade Mapping_[{}]::design_geos".format(self.selected_session_name))
        

        for layer in rs.LayerNames():
            if layer.startswith("EA_Facade Mapping_") and "::" not in layer:
                rs.LayerVisible(layer, False)
        rs.EnableRedraw(True)


    @ERROR_HANDLE.try_catch_error
    def delete_session_click(self, sender, e):
        if not self.selected_session_name:
            NOTIFICATION.messenger(main_text= "No session selected")
            
            return
        
        
        opts = ["DELETE!", "Cancel"]
        result = rs.ListBox(opts, 
                            "Are you sure you want to delete session\n<{}>?".format(self.selected_session_name),
                            title="Oh you are about to delete a session...")
        if result != opts[0]:
            return
        
        
        rs.EnableRedraw(False)
        for layer in rs.LayerNames():
            if not layer.startswith("EA_Facade Mapping_"):
                rs.CurrentLayer(layer)
                break
            
        for layer in rs.LayerNames():
            if layer.startswith("EA_Facade Mapping_[{}]".format(self.selected_session_name)):
                if rs.IsLayer(layer):
                    rs.PurgeLayer(layer)
                
        rs.EnableRedraw(True)
        self.reset_listbox()
                
        
        
    @property
    def selected_session_name(self):
        index = self.session_name_list.SelectedIndex
        if index < 0:
            return None
        
        return self.session_name_list.Items[index]
    

        
    def zoom_objs_by_layers(self,layers):
        if not isinstance(layers, list):
            layers = [layers]
                                 
        objs = []  
        for layer in layers:
            objs += rs.ObjectsByLayer(layer)
        
        if len(objs) == 0:
            NOTIFICATION.messenger(main_text= "There is no geometry to zoom")
            return
        
        rs.EnableRedraw(False)
        rs.UnselectAllObjects()
        rs.SelectObjects(objs)
        rs.ZoomSelected()
        rs.UnselectAllObjects()
        rs.EnableRedraw(True)
            
           
    @ERROR_HANDLE.try_catch_error
    def on_zoom_design_area_click(self, sender, e):
        focus_layers = [x for x in rs.LayerNames() if x.startswith("EA_Facade Mapping_[{}]::design_geos".format(self.selected_session_name))]

        self.zoom_objs_by_layers(focus_layers)
        
    @ERROR_HANDLE.try_catch_error
    def on_zoom_mapped_area_click(self, sender, e):
        focus_layers = [x for x in rs.LayerNames() if x.startswith("Mapped_Facade_[{}]".format(self.selected_session_name))]

        self.zoom_objs_by_layers(focus_layers)
            
    def get_all_session_names(self):
        all_layers = rs.LayerNames()
        layers = [x.split("::")[0]  for x in all_layers if x.startswith("EA_Facade Mapping")]
        layers = [x.split("[")[1].split("]")[0]  for x in layers] 
       
        return sorted(list(set(layers)))

    def CreateButtons(self):

        user_buttons = []
   

        user_buttons.append(None)
        
   
        
        self.btn_morph = Eto.Forms.Button()
        self.btn_morph.Height = 30
        self.btn_morph.Text = " Morph! "
        
  
        temp_bitmap = Eto.Drawing.Bitmap("{}\\morph.png".format(os.path.dirname(os.path.realpath(__file__))))
        self.btn_morph.Image = temp_bitmap.WithSize(200,50)
        self.btn_morph.Image = temp_bitmap
        self.btn_morph.ImagePosition = Eto.Forms.ButtonImagePosition.Left
        self.btn_morph.Click += self.btn_morph_action
        
        
        
        self.btn_delete_session = Eto.Forms.Button()
        self.btn_delete_session.Height = 30
        self.btn_delete_session.Text = " Delete Session "
        self.btn_delete_session.Click += self.delete_session_click
        
        
        user_buttons.append(self.btn_morph)
        user_buttons.append( self.btn_delete_session)

        user_buttons.append(None)

        return user_buttons




    @ERROR_HANDLE.try_catch_error
    def btn_morph_action(self, sender, e):
        if not self.selected_session_name:
            NOTIFICATION.messenger(main_text = "Need a selected session name.")
            return
        
        if not self.offset_data:
            return
        
        Morph_Solution(None, self.selected_session_name, self.offset_data).morph_along_srf()




    


    @ERROR_HANDLE.try_catch_error
    def btn_pick_new_srf(self, sender, e):
        session_name = self.tbox_session_name.Text
        if not session_name:
            NOTIFICATION.messenger(main_text = "Need a session name.")
            return
        if session_name in self.get_all_session_names():
            NOTIFICATION.messenger(main_text = "Session name already exists.")
            return
        if not self.offset_data:
            return
        
        NOTIFICATION.messenger(main_text = "Pick your input surf.")
        srf = rs.GetObject("Pick a surface.", filter = 8)
        
   
        geo = rs.coercesurface(srf)
        if hasattr(geo, "IsCappedAtBottom"):
            NOTIFICATION.messenger(main_text = "Please use srf, not extrusion.")
            return

        
        if srf:
            
            temp_note = "Ref surface picked!"
            self.srf_label.Text = temp_note
            NOTIFICATION.messenger(main_text = temp_note)

            Morph_Solution(srf, session_name, self.offset_data)
            self.reset_listbox()
            
        else:
            temp_note = "Ref surface NOT picked!"
            self.srf_label.Text = temp_note
            NOTIFICATION.messenger(main_text = temp_note)


    @property
    def offset_data(self):
        try:
            return (int(self.tbox_design_ref_offset_x.Text),
                int(self.tbox_design_target_offset_x.Text),
                int(self.tbox_design_target_offset_z.Text))
        except:
            NOTIFICATION.messenger(main_text = "Offset data is not valid.")
            return None
        

    @ERROR_HANDLE.try_catch_error
    def OnFormClosed(self, sender, e):
        self.Close()


    @ERROR_HANDLE.try_catch_error
    def InitiateFiller(self):
        # use this filler to control what to record and preload for UI setting

        
        for x in self.ui_input:
            sticky_key = FORM_KEY + x
            if not hasattr(self, x):
                continue
            user_input_ui = getattr(self, x)
            
            
            if "tbox" in x:
                value = DATA_FILE.get_sticky_longterm(sticky_key, "")
                setattr(user_input_ui, "Text", value)
            elif "tbox_design" in x:
                value = DATA_FILE.get_sticky_longterm(sticky_key, "500")
                setattr(user_input_ui, "Text", value)
            elif "checkbox" in x:
                value = DATA_FILE.get_sticky_longterm(sticky_key, False)
                setattr(user_input_ui, "Checked", value)
 
        return


    @ERROR_HANDLE.try_catch_error
    def Close(self):
      
        # Dispose of the form and remove it from the sticky dictionary
        if sc.sticky.has_key(FORM_KEY):
            form = sc.sticky[FORM_KEY]
            if form:
                form.Dispose()
                form = None
            sc.sticky.Remove(FORM_KEY)

        for x in self.ui_input:
            if not hasattr(self, x):
                continue
            user_input_ui = getattr(self, x)
            sticky_key = FORM_KEY + x
            #print x
            if hasattr(user_input_ui,"Text"):
                DATA_FILE.set_sticky_longterm(sticky_key, user_input_ui.Text)
            if hasattr(user_input_ui,"Checked"):
                DATA_FILE.set_sticky_longterm(sticky_key, user_input_ui.Checked)





def shape_mapper():
    rs.EnableRedraw(False)

    if sc.sticky.has_key(FORM_KEY):
        return
    dlg = ShapeMapperDialog()
    dlg.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    dlg.Show()
    sc.sticky[FORM_KEY] = dlg
    

