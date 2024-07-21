
__title__ = "AiRenderUpscale"
__doc__ = "Upscale AI generated images."

import time
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Eto # pyright: ignore
import os

from EnneadTab import NOTIFICATION, EXE, DATA_FILE, FOLDER, TIME
from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_UI


class RenderUpscalerDialog(Eto.Forms.Form):
    def get_all_session_folders(self):
        # print os.listdir(self.root_folder)
        return  [os.path.join(self.root_folder, folder) for folder in os.listdir(self.root_folder) ]
    
    def get_most_recent_session_folder(self):
        most_recent_folder = None
        most_recent_time = None
        for folder in self.get_all_session_folders():
            
            folder_time = os.path.getctime(folder)
            if most_recent_time is None or folder_time > most_recent_time:
                most_recent_folder = folder
                most_recent_time = folder_time
                
        return most_recent_folder
    
    
    # Class initializer
    def __init__(self):
        self.root_folder = "{}\Documents\EnneadTab Settings\Local Copy Dump\EnneadTab_Ai_Rendering".format(os.environ["USERPROFILE"])

        # print self.root_folder
        # print self.get_all_session_folders()
        

        

                
                
        self.session_folder = self.get_most_recent_session_folder()
        self.session_index = self.get_all_session_folders().index(self.session_folder)
        self.selected_index = 0
        self.preview_file = None
        # self.previous_data = None




        # Initialize dialog box
        self.Title = 'Ai Rendering Upscaler.'
        self.Padding = Eto.Drawing.Padding(10)
        # Create a table layout and add all the controls
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(10)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        layout.AddSeparateRow(None, self.CreateLogoImage())
        layout.AddRow(self.CreateFolderButtons())
        layout.AddRow(self.CreateLabel())
        layout.AddRow(self.CreateImageView())
        layout.AddRow(self.CreateSessionPickerButtons())
        layout.AddRow(None) # spacer
        layout.AddRow(self.CreateInputBox()) # spacer
        layout.AddRow(self.CreateButtons())
        # Set the dialog content
        self.Content = layout
        self.update_preview()



        self.Closed += self.OnFormClosed
        
        RHINO_UI.apply_dark_style(self)

            # Form Closed event handler
    def OnFormClosed(self, sender, e):
        
        self.Close()
        
    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        return self.logo
    

    # Create the dialog label
    def CreateLabel(self):
        layout = Eto.Forms.DynamicLayout()
        self.m_label = Eto.Forms.Label(Text = 'No Session Folder Picked')
        layout.AddSeparateRow(None, self.m_label, None)
        return layout
    

    # Create the dialog image list
    def CreateImageView(self):
        self.m_image_view = Eto.Forms.ImageView()
        self.initial_w, self.initial_h = 500, 400
        self.m_image_view.Size = Eto.Drawing.Size(self.initial_w, self.initial_h)
        self.m_image_view.Image = None

        
        return self.m_image_view
    

    def CreateFolderButtons(self):
        layout = Eto.Forms.DynamicLayout()
        self.bt_open_folder = Eto.Forms.Button(Text = 'Open Session Folder')
        self.bt_open_folder.Click += self.OnOpenFolderButtonClick
        bt_delete_session = Eto.Forms.Button(Text = 'Delete Session')
        bt_delete_session.Click += self.OnDeleteSessionButtonClick
        layout.AddSeparateRow(None, bt_delete_session, self.bt_open_folder)
        return layout

    
    def CreateSessionPickerButtons(self):
        layout = Eto.Forms.DynamicLayout()
        self.bt_pick_session_folder = Eto.Forms.Button(Text = ' Pick Session Folder ')
        self.bt_pick_session_folder.Click += self.OnPickSessionFolderButtonClick

        bt_session_left = Eto.Forms.Button(Text = ' << ')
        bt_session_left.Click += self.OnSessionLeftButtonClick
        bt_session_right = Eto.Forms.Button(Text = ' >> ')
        bt_session_right.Click += self.OnSessionRightButtonClick
        
        bt_left = Eto.Forms.Button(Text = ' < ')
        bt_right = Eto.Forms.Button(Text = ' > ')
        bt_left.Click += self.OnPreviewLeftButtonClick
        bt_right.Click += self.OnPreviewRightButtonClick
        layout.AddSeparateRow(bt_session_left,
                              None, 
                              bt_left, 
                              self.bt_pick_session_folder, 
                              bt_right, 
                              None,
                              bt_session_right)

        return layout



    def CreateInputBox(self):
        layout = Eto.Forms.DynamicLayout()
   

        self.previous_model_label = Eto.Forms.Label(Text = '')
        self.previous_model_label.TextAlignment = Eto.Forms.TextAlignment.Center
        layout.AddRow(self.previous_model_label)



        label = Eto.Forms.Label(Text = '\nPositive prompts used here:')
        layout.AddRow(label)
        self.tbox_positive_prompts = Eto.Forms.TextArea()
        self.tbox_positive_prompts.Size = Eto.Drawing.Size(500, 100)
        self.tbox_positive_prompts.Text = ""

        layout.AddRow(self.tbox_positive_prompts)


        layout.AddRow(None)
        label = Eto.Forms.Label(Text = '\nNegative prompts used here:')
        #layout.AddRow(label)
        self.tbox_negative_prompts  = Eto.Forms.TextArea()
        self.tbox_negative_prompts.Size = Eto.Drawing.Size(500, 100)
        self.tbox_negative_prompts.Text = ""
        #layout.AddRow(self.tbox_negative_prompts)


        layout.AddRow(None)
        label = Eto.Forms.Label(Text = 'Num of Output Images: ')
        self.tbox_num_of_img = Eto.Forms.TextBox()
        self.tbox_num_of_img.Text = '1'
        self.tbox_num_of_img.Width = 30
        self.tbox_num_of_img.TextAlignment  = Eto.Forms.TextAlignment .Center
        label2 = Eto.Forms.Label(Text = '(The higher the number, the more GPU space is needed.)')
        layout.AddSeparateRow(label, self.tbox_num_of_img, None, label2)

        layout.AddRow(None)
        label = Eto.Forms.Label(Text = 'Resolution: W x H factor.')
        layout.AddRow(label)
        
        self.tbox_scale_factor = Eto.Forms.TextBox()
        self.tbox_scale_factor.Text = '4'
        self.tbox_scale_factor.Width = 30
        self.tbox_scale_factor.TextAlignment  = Eto.Forms.TextAlignment .Center

        self.label_preview_resolution = Eto.Forms.Label()
        self.label_preview_resolution.Text = ""
        self.label_target_resolution = Eto.Forms.Label()
        self.label_target_resolution.Text = ""
        bt_update_resolution = Eto.Forms.Button(Text = 'Update Factor Resolution')
        bt_update_resolution.Click += self.OnUpdateResolutionButtonClick

        layout.AddSeparateRow(self.label_preview_resolution, 
                              Eto.Forms.Label(Text = ' x '), 
                              self.tbox_scale_factor, 
                              Eto.Forms.Label(Text = ' = '),
                              self.label_target_resolution,
                              None, bt_update_resolution)
    
        return layout
    

    # Create the dialog buttons
    def CreateButtons(self):

        self.bt_export = Eto.Forms.Button(Text = 'Send to AI to Upscale')
        self.bt_export.Click += self.OnExportButtonClick

        # Create the abort button
        self.AbortButton = Eto.Forms.Button(Text = 'Close')
        self.AbortButton.Click += self.OnCloseButtonClick
        # Create button layout
        button_layout = Eto.Forms.DynamicLayout()
        button_layout.Spacing = Eto.Drawing.Size(5, 5)

        button_layout.AddRow( None, self.bt_export, self.AbortButton)

        return button_layout
        

    
    def OnPickSessionFolderButtonClick(self, sender, e):
        self.session_folder = rs.BrowseForFolder(self.root_folder, title = "Pick session folder.")
        if self.session_folder is None:
            return
        self.selected_index = 0

        self.update_preview()

    @property
    def previous_data(self):
        return DATA_FILE.read_json_as_dict(os.path.join(self.session_folder, "EnneadTab AI Meta Data.sexyDuck"))

    
    
    def OnPreviewLeftButtonClick(self, sender, e):

        self.selected_index -= 1
        self.update_preview()

    
    def OnPreviewRightButtonClick(self, sender, e):
        self.selected_index += 1
        self.update_preview()

    
    def OnSessionLeftButtonClick(self, sender, e):
        self.session_index -= 1
        all_session_folder = self.get_all_session_folders()
        self.session_index  = self.session_index % len(all_session_folder)
        self.session_folder = all_session_folder[self.session_index]
        self.update_preview()
        
    
    def OnSessionRightButtonClick(self, sender, e):
        self.session_index += 1
        all_session_folder = self.get_all_session_folders()
        self.session_index  = self.session_index % len(all_session_folder)
        self.session_folder = all_session_folder[self.session_index]
        self.update_preview()    
        


    def OnUpdateResolutionButtonClick(self, sender, e):
        self.update_preview()


    def OnOpenFolderButtonClick(self, sender, e):
        try:
            os.startfile(self.session_folder)
            
            # os.startfile("{}\Documents\EnneadTab Settings\Local Copy Dump\EnneadTab_Ai_Rendering".format(os.environ["USERPROFILE"]))
        except:
            print ("Folder not exist, please wait")

    def update_preview(self):
        if self.session_folder is None:
            return
        
        if self.previous_data:
            self.tbox_positive_prompts.Text = self.previous_data["positive_prompt"]
            self.tbox_negative_prompts.Text = self.previous_data["negative_prompt"]
            try:
                self.previous_model_label.Text = "Pipline model used = " + self.previous_data.get("model_name", "Unknown").replace( "S:\SD-Model\\", "")
            except:
                self.previous_model_label.Text = "Pipline model used = Unknown"
        else:
            self.tbox_positive_prompts.Text = ""
            self.tbox_negative_prompts.Text = ""
            self.previous_model_label.Text = "Pipline model used = Unknown"
        

        files = [file for file in os.listdir(self.session_folder) if "AI_" in file or "Original" in file]

        if len(files) == 0:
            self.selected_index = 0
        else:
            self.selected_index = self.selected_index % len(files)
        self.preview_file = os.path.join(self.session_folder, files[self.selected_index])
    


 

        
        self.m_image_view.Image = Eto.Drawing.Bitmap(self.preview_file)
            # Update the text label
        self.m_label.Text = 'Preview: {} in folder <{}>'.format(files[self.selected_index], self.session_folder.split("\\")[-1])
        
        old_w, old_h = self.m_image_view.Image.Size.Width, self.m_image_view.Image.Size.Height
        new_w, new_h = old_w * int(self.tbox_scale_factor.Text), old_h * int(self.tbox_scale_factor.Text)
        old_w, old_h = str(old_w), str(old_h)
        new_w, new_h = str(new_w), str(new_h)
        self.label_preview_resolution.Text = "(" + old_w + " x " + old_h + ")"
        self.label_target_resolution.Text = "(" + new_w + " x " + new_h + ")"
        
        
        
        w, h = self.m_image_view.Image.Size.Width, self.m_image_view.Image.Size.Height

        if h != self.initial_h:
            factor = float(h) / self.initial_h
            h = self.initial_h
            w = int(w / factor)
        
        self.m_image_view.Size = Eto.Drawing.Size(w, h)
  
    
    
    def OnDeleteSessionButtonClick(self, sender, e):
        if self.session_folder is None:
            return
        

        print ("Delete session folder: ", self.session_folder)
        import shutil
        shutil.rmtree(self.session_folder)




    
    def OnExportButtonClick(self, sender, e):
        self.session = time.strftime("%Y%m%d-%H%M%S")
       
        self.send_data()

    # Close button click handler
    def OnCloseButtonClick(self, sender, e):
        self.Close()
        


    @property
    def input_image_filename(self):
        main_folder = FOLDER.get_EA_local_dump_folder()
        session_folder = main_folder + "\\EnneadTab_Ai_Rendering\\Session_{}_Upscale".format(self.session)
        if not os.path.exists(session_folder):
            os.makedirs(session_folder)

        return os.path.join(session_folder, "Original.jpeg")

    # Returns the captured image
    def Image(self):


        return self.m_image_view.Image
    
    def Close(self):
        # Dispose of the form and remove it from the sticky dictionary
        if sc.sticky.has_key('EA_AI_RENDER_UPSCALER_FORM'):
            form = sc.sticky['EA_AI_RENDER_UPSCALER_FORM']
            if form:
                form.Dispose()
                form = None
            sc.sticky.Remove('EA_AI_RENDER_UPSCALER_FORM')

 

    
    def send_data(self):
        if not self.preview_file:
            return
        data = dict()
        data["session"] = self.session
        data["input_image"] = self.preview_file

 


        data["positive_prompt"] = self.tbox_positive_prompts.Text
        data["negative_prompt"] = self.tbox_negative_prompts.Text
        data["number_of_output"] = int(self.tbox_num_of_img.Text)

        # match pattern of (w x h) to get the string of w and h as int
        import re
        match = re.search(r"\((\d+)\s+x\s+(\d+)\)", self.label_target_resolution.Text)
        w, h = int(match.group(1)), int(match.group(2))
        data["desired_resolution"] = [w, h]
        data["direction"] = "IN"


        DATA_FILE.set_data(data, "AI_RENDER_SCALER_{}.sexyDuck".format(TIME.get_formatted_current_time()))

        NOTIFICATION.messenger(main_text = "Upscale Job Enqueued!") 
        call_exe()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def render_upscale():
    # See if the form is already visible
    if sc.sticky.has_key('EA_AI_RENDER_UPSCALER_FORM'):
        return
    
    # Create and show form
    form = RenderUpscalerDialog()
    form.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    form.Show()
    # Add the form to the sticky dictionary so it
    # survives when the main function ends.
    sc.sticky['EA_AI_RENDER_UPSCALER_FORM'] = form


def call_exe():

    EXE.try_open_app("EA_AI_SCALER")

 

if __name__ == "__main__":
    render_upscale()