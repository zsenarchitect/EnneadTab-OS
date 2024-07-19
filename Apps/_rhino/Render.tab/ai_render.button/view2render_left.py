
__title__ = "AiRenderingFromView"
__doc__ = "Render captured Rhino view with Stable Diffusion."


import time


import Rhino # pyright: ignore
import scriptcontext as sc
import Eto # pyright: ignore
import os
import System # pyright: ignore
import random

from EnneadTab import USER, FOLDER, NOTIFICATION, DATA_FILE, EXE, TIME
from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_UI

MODEL_DICT = {0: "runwayml/stable-diffusion-v1-5"}
# get all file in a folder
MODEL_FOLDER = "L:\\4b_Applied Computing\SD-Model"  # "S:\SD-Model"
files = [file for file in os.listdir(MODEL_FOLDER) if file != "source"]

# https://civitai.com/?tag=buildings
APPROVED_MODEL = ["architecturerealmix_v10",
                  "xsarchitectural_v11",
                  "xsarchitecturalv3com_v3",
                  "productDesign_eddiemauro20",
                  "MrMcFanyongV1512_mrMcFanyongV1512",
                  "majicmixRealistic_v6",
                  "lofi_v3",
                  "landscapesupermix_v2",
                  "interiordesignsuperm_v2",
                  "dvarchMultiPrompt_dvarchExterior",
                  "colorful_v31",
                  "cetusMix_Whalefall2",
                  "yqModernexclusive_v10"]

UNAPPROVED_MODEL = [file for file in files if file not in APPROVED_MODEL]
files = ["---- base pipeline above ----"] + APPROVED_MODEL + \
    ["---- archi good above, less good below ----"] + UNAPPROVED_MODEL
"""
unknown:


bad ones:
ttslbArchiV1_v10

"""


"""
Note to furture

 do a test runner to try all the pipline model
   and give a list that cannot work and model that can work
"""


if not USER.IS_DEVELOPER:
    files = [file for file in files if file in APPROVED_MODEL]
for i, model in enumerate(files):

    # remove the extenion in model name
    # model = model.split(".")[0]
    MODEL_DICT[i + 1] = model  # os.path.join(folder, model)
# MODEL_DICT[len(MODEL_DICT.keys())] = "stabilityai\stable-diffusion-2-1"
# print MODEL_DICT

PROMPT_DICT = {}
PROMPT_DICT["00_general_mode"] = ["Exterior",
                                  "Interior",
                                  "Site Plan",
                                  "Floor Plan",
                                  "Elevation"]

PROMPT_DICT["01_style_mode"] = ["Professional Architecture Rendering",
                                "Architecture Diagram",
                                "Architectural Photography",
                                "Architecture Illustration",
                                "Architectural physical model"]
PROMPT_DICT["02_typology_mode"] = ["Residential Building",
                                   "Office Building",
                                   "Industrial Building",
                                   "Office Space",
                                   "Industrial Space",
                                   "Residential Space",
                                   "Train Station",
                                   "Museum",
                                   "City Plaza",
                                   "High School",
                                   "Univeristy",
                                   "Playground",
                                   "Retail",
                                   "Shopping Center",
                                   "Storefront Shopping",
                                   "Waterfront parking",
                                   "Parking garage"]
PROMPT_DICT["03_scale_mode"] = ["Villa",
                                "Lowrise",
                                "Highrise",
                                "Super Tall",
                                "Skyscraper",
                                "Town House",
                                "Master Plannings",
                                "City",
                                "Planet",
                                "Stars",
                                "Intersteller"]

PROMPT_DICT["04_reference_mode"] = ["archdaily.com",
                                    "pritzker winner",
                                    "award-winning",
                                    "MOMA",
                                    "Iwan Baan",
                                    "NASA",
                                    "Aliens"]
PROMPT_DICT["05_design_mode"] = ["Modern",
                                 "Classic",
                                 "Traditional",
                                 "Artistic",
                                 "Modern Art",
                                 "Minimalism",
                                 "Organic",
                                 "Very Organic",
                                 "Sharp Edges"]

PROMPT_DICT["10_lighting_mode"] = ["Natrual light",
                                   "Sun light",
                                   "HDR",
                                   "HDR+",
                                   "Morning Light",
                                   "Sunset lighting",
                                   "Dusk Light",
                                   "Dramatic Lighting"]
PROMPT_DICT["11_wheather_mode"] = ["Sunny",
                                   "Cloudy",
                                   "Rainy",
                                   "Windy",
                                   "Snowy",
                                   "After Rain",
                                   "Foggy"]
PROMPT_DICT["12_color_mode"] = ["Black and White",
                                "All white material",
                                "accent orange color"]

PROMPT_DICT["20_country_mode"] = ["Canada",
                                  "United States",
                                  "Mexico",
                                  "United Kingdom",
                                  "France",
                                  "Germany",
                                  "Italy",
                                  "Spain",
                                  "Australia",
                                  "Japan",
                                  "Singapore",
                                  "China"]
PROMPT_DICT["21_city_mode"] = ["City",
                               "city center",
                               "Suburbs",
                               "Towns",
                               "Villages",
                               "Urban",
                               "park",
                               "urban plaza"]
PROMPT_DICT["22_region_mode"] = ["North America",
                                 "South America",
                                 "Europe",
                                 "Asia",
                                 "Africa",
                                 "Australia",
                                 "Antarctica"]

PROMPT_DICT["30_mood_mode"] = ["Happy",
                               "Sad",
                               "Angry",
                               "Surprised",
                               "Disgusted",
                               "Fearful",
                               "Neutral",
                               "Peaceful",
                               "Exciting",
                               "futuristic",
                               "dreammy"]
PROMPT_DICT["31_people_mode"] = ["Crowded",
                                 "No people",
                                 "Office people",
                                 "Party people",
                                 "pedestrian friendly"]
PROMPT_DICT["32_age_mode"] = ["Young",
                              "Middle aged",
                              "Old",
                              "brand new",
                              "future"]

PROMPT_DICT["40_material_mode"] = ["Wood",
                                   "Yellow Copper",
                                   "Blue Plastic",
                                   "Blurry Glass",
                                   "Reflective glass",
                                   "Fine Leather",
                                   "Cloth",
                                   "Fabric", "Paper"]

PROMPT_DICT["99_must_have"] = ["Best Quality",
                               "Very Detailed",
                               "Fine texture"]


class ViewCaptureDialog(Eto.Forms.Form):

    # Class initializer
    def __init__(self):
        # Initialize dialog box
        self.Title = 'View2Ai Rendering.'
        self.Padding = Eto.Drawing.Padding(10)
        # Create a table layout and add all the controls
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(10)
        layout.Spacing = Eto.Drawing.Size(5, 5)
        layout.AddSeparateRow(None, self.CreateLogoImage())
        layout.AddRow(self.CreateFolderButtons())
        layout.AddRow(self.CreateLabel())
        layout.AddRow(self.CreateImageView())
        layout.AddRow(None)  # spacer
        layout.AddRow(self.CreateInputBox())  # spacer
        layout.AddRow(self.CreateButtons())
        # Set the dialog content
        self.Content = layout
        self.capture_view()

        self.Closed += self.OnFormClosed
        
        
        RHINO_UI.apply_dark_style(self)

        # Form Closed event handler
    def OnFormClosed(self, sender, e):

        self.Close()

    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        self.FOLDER_PRIMARY = r"L:\4b_Applied Computing\00_Asset Library"
        self.FOLDER_APP_IMAGES = r"{}\Database\app images".format(
            self.FOLDER_PRIMARY)
        self.LOGO_IMAGE = r"{}\Ennead_Architects_Logo.png".format(
            self.FOLDER_APP_IMAGES)
        temp_bitmap = Eto.Drawing.Bitmap(self.LOGO_IMAGE)
        self.logo.Image = temp_bitmap.WithSize(200, 30)
        return self.logo

    # Create the dialog label

    def CreateLabel(self):
        self.m_label = Eto.Forms.Label(Text='Click the "Capture" button...')
        return self.m_label

    # Create the dialog image list

    def CreateImageView(self):
        self.m_image_view = Eto.Forms.ImageView()
        self.initial_w, self.initial_h = 500, 400
        self.m_image_view.Size = Eto.Drawing.Size(
            self.initial_w, self.initial_h)
        self.m_image_view.Image = None

        return self.m_image_view

    def CreateFolderButtons(self):
        layout = Eto.Forms.DynamicLayout()
        self.bt_open_folder = Eto.Forms.Button(Text='Open OutputFolder')
        self.bt_open_folder.Click += self.OnOpenFolderButtonClick

        bt_test_model = Eto.Forms.Button(Text="Test Unapproved Models")
        bt_test_model.Click += self.OnTestModelButtonClick
        if USER.IS_DEVELOPER:
            layout.AddSeparateRow(None, bt_test_model,  self.bt_open_folder)
        else:
            layout.AddSeparateRow(None, self.bt_open_folder)
        return layout

    @property
    def sample_prompt(self):
        # "architecture exterior rendering, professional, archdaily.com, japanese architects, peaceful, few people, city center, after rain, dusk, high resolution, european modern architects, very detailed, natural lighting, award-winning, highest quality, sci-fi, natural material."
        sample_prompt = ""
        for mode in sorted(PROMPT_DICT.keys()):
            # random sample from list
            sample_count = 1
            if mode == "99_must_have":
                sample_count = 2
            elif mode == "40_material_mode":
                sample_count = 3
            values = random.sample(PROMPT_DICT[mode], sample_count)
            for value in values:
                sample_prompt += "{}, ".format(value)

        return sample_prompt.rstrip(", ")

    def CreateInputBox(self):
        layout = Eto.Forms.DynamicLayout()

        # multiline_textbox = Eto.Forms.TextArea()
        # multiline_textbox.Text = "Hello, world!"
        # multiline_textbox.Size = Eto.Drawing.Size(200, 200)
        # layout.AddRow(multiline_textbox)
        label = Eto.Forms.Label(Text='Pick a Model:')
        label2 = Eto.Forms.Label(
            Text='Rendering will happen in the background and will take GPU resource.\nBut your Rhino is free to continue working.')
        self.cb_model = Eto.Forms.ComboBox()
        self.cb_model.DataStore = MODEL_DICT.values()
        # get the key of the dict whose value is "architecturerealmix_v10"
        self.cb_model.SelectedIndex = MODEL_DICT.keys(
        )[MODEL_DICT.values().index("architecturerealmix_v10")]
        # self.cb_model.SelectedIndex = 1
        layout.AddSeparateRow(label, self.cb_model)
        layout.AddSeparateRow(label2)

        label = Eto.Forms.Label(Text='\nEnter below the positive prompts:')
        layout.AddRow(label)
        self.tbox_positive_prompts = Eto.Forms.TextArea()
        self.tbox_positive_prompts.Size = Eto.Drawing.Size(500, 100)
        self.tbox_positive_prompts.Text = self.sample_prompt
        layout.AddRow(self.tbox_positive_prompts)

        layout.AddRow(None)
        label = Eto.Forms.Label(Text='\nEnter below the negative prompts:')
        layout.AddRow(label)
        self.tbox_negative_prompts = Eto.Forms.TextArea()
        self.tbox_negative_prompts.Size = Eto.Drawing.Size(500, 50)
        self.tbox_negative_prompts.Text = "cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, blurry, bad anatomy, bad proportions"
        layout.AddRow(self.tbox_negative_prompts)

        layout.AddRow(None)
        label = Eto.Forms.Label(Text='Num of Output Images: ')
        self.tbox_num_of_img = Eto.Forms.TextBox()
        self.tbox_num_of_img.Text = '4'
        self.tbox_num_of_img.TextAlignment = Eto.Forms.TextAlignment .Center
        self.tbox_num_of_img.Width = 30
        label2 = Eto.Forms.Label(
            Text='(Keep it low for best GPU performance.)')
        layout.AddSeparateRow(label, self.tbox_num_of_img, None, label2)

        layout.AddRow(None)
        label = Eto.Forms.Label(Text='Resolution: W x H: ')
        self.tbox_width = Eto.Forms.TextBox()
        self.tbox_width.Text = '500'
        self.tbox_width.TextAlignment = Eto.Forms.TextAlignment .Center
        self.tbox_width.Width = 40
        self.tbox_height = Eto.Forms.TextBox()
        self.tbox_height.Text = '400'
        self.tbox_height.TextAlignment = Eto.Forms.TextAlignment .Center
        self.tbox_height.Width = 40
        layout.AddSeparateRow(label, self.tbox_width, Eto.Forms.Label(
            Text=' x '), self.tbox_height, None)

        layout.AddRow(None)
        label = Eto.Forms.Label(Text='Step of Iteration: ')
        self.tbox_iteration = Eto.Forms.TextBox()
        self.tbox_iteration.Text = '50'
        self.tbox_iteration.TextAlignment = Eto.Forms.TextAlignment .Center
        self.tbox_iteration.Width = 30

        label2 = Eto.Forms.Label(Text='Similarity: ')
        self.weight_slider = Eto.Forms.Slider()
        self.weight_slider.MaxValue = 100
        self.weight_slider.MinValue = 0
        self.weight_slider.Value = 50
        self.weight_slider.SnapToTick = True
        self.weight_slider.TickFrequency = 10
        self.weight_slider.ValueChanged += self.OnSliderChanged
        self.weight_slider_label = Eto.Forms.Label(
            Text='{}%'.format(self.weight_slider.Value))
        layout.AddSeparateRow(label, self.tbox_iteration, None,
                              label2, self.weight_slider, self.weight_slider_label)

        layout.AddSeparateRow(None, Eto.Forms.Label(
            Text="Note: If you want to export in high resolution, set output count to 1.\nIf you want to export more output options, set the resolution to below 1000 in either direction."), None)

        if USER.IS_DEVELOPER:
            self.foundation_pipeline_list = Eto.Forms.RadioButtonList()
            self.foundation_pipeline_list.Orientation = Eto.Forms.Orientation.Vertical
            self.foundation_pipeline_list.DataStore = [
                "Edge Detection", "Style Match Reference Image", "In Paint"]
            self.foundation_pipeline_list.SelectedValue = self.foundation_pipeline_list.DataStore[
                0]
            self.foundation_pipeline_list.SelectedValueChanged += self.foundation_pipeline_changed
            self.bt_load_external_image = Eto.Forms.Button(
                Text='Load External Image')
            layout.AddSeparateRow(
                self.foundation_pipeline_list, None, self.bt_load_external_image)
        return layout

    # Create the dialog buttons

    def CreateButtons(self):
        # Create the default button
        self.bt_capture = Eto.Forms.Button(Text='Update View Capture')
        self.bt_capture.Click += self.OnCaptureButtonClick

        self.bt_export = Eto.Forms.Button(Text='Send to AI')
        self.bt_export.Click += self.OnExportButtonClick

        # Create the abort button
        self.AbortButton = Eto.Forms.Button(Text='Close')
        self.AbortButton.Click += self.OnCloseButtonClick
        # Create button layout
        button_layout = Eto.Forms.DynamicLayout()
        button_layout.Spacing = Eto.Drawing.Size(5, 5)

        button_layout.AddRow(self.bt_capture, None,
                             self.bt_export, self.AbortButton)

        return button_layout

    def OnOpenFolderButtonClick(self, sender, e):
        try:
            os.startfile("{}\Documents\EnneadTab Settings\Local Copy Dump\EnneadTab_Ai_Rendering".format(
                os.environ["USERPROFILE"]))
        except:
            print("Folder not exist, please wait")

    def capture_view(self):
        # Capture the active view to a System.Eto.Drawing.Bitmap
        view = sc.doc.Views.ActiveView
        original_size = view.Size
        w = int(self.tbox_width.Text)
        h = int(self.tbox_height.Text)

        if h != self.initial_h:
            factor = float(h) / self.initial_h
            h = self.initial_h
            w = int(w / factor)
        # if w > self.initial_w:
        #     factor = w / self.initial_w
        #     w = self.initial_w
        #     h = int(h / factor)
        view.Size = System.Drawing.Size(w, h)

        self.m_image_view.Image = Rhino.UI.EtoExtensions.ToEto(
            view.CaptureToBitmap())
        self.m_image_view.Size = Eto.Drawing.Size(w, h)
        view.Size = original_size
        # Update the text label
        self.m_label.Text = 'Captured view: {}'.format(
            view.ActiveViewport.Name)
        # Disable the default button
        self.bt_capture.Enabled = True


    def foundation_pipeline_changed(self, sender, e):
        if self.foundation_pipeline_list.SelectedIndex != 0:
            self.bt_load_external_image.Enabled = True
        else:
            self.bt_load_external_image.Enabled = False

    # Capture button click handler


    def OnCaptureButtonClick(self, sender, e):
        self.capture_view()


    def OnExportButtonClick(self, sender, e):
        self.session = time.strftime("%Y%m%d-%H%M%S")
        self.save_capture_to_file()
        self.send_data()

    # Close button click handler
    def OnCloseButtonClick(self, sender, e):
        self.Close()

    def OnSliderChanged(self, sender, e):
        self.weight_slider_label.Text = '{}%'.format(self.weight_slider.Value)


    def OnTestModelButtonClick(self, sender, e):
        print(UNAPPROVED_MODEL)

        for i, model in enumerate(UNAPPROVED_MODEL):
            print("{}/{}--testing model: {}".format(i +
                  1, len(UNAPPROVED_MODEL), model))
            self.session = "Model Test_{}".format(
                time.strftime("%Y%m%d-%H%M%S"))
            self.cb_model.SelectedIndex = MODEL_DICT.keys(
            )[MODEL_DICT.values().index(model)]
            self.save_capture_to_file()
            self.send_data()
            time.sleep(2)

    @property
    def input_image_filename(self):
        main_folder = FOLDER.get_EA_local_dump_folder()
        session_folder = main_folder + \
            "\\EnneadTab_Ai_Rendering\\Session_{}".format(self.session)
        if not os.path.exists(session_folder):
            os.makedirs(session_folder)

        return os.path.join(session_folder, "Original.jpeg")

    # Returns the captured image
    def Image(self):

        return self.m_image_view.Image

    def Close(self):
        # Dispose of the form and remove it from the sticky dictionary
        if sc.sticky.has_key('EA_AI_RENDER_CAPTURE_FORM'):
            form = sc.sticky['EA_AI_RENDER_CAPTURE_FORM']
            if form:
                form.Dispose()
                form = None
            sc.sticky.Remove('EA_AI_RENDER_CAPTURE_FORM')

    def save_capture_to_file(self):
        view = sc.doc.Views.ActiveView
        view_capture = Rhino.Display.ViewCapture()
        # view_capture.Width = view.ActiveViewport.Size.Width
        # view_capture.Height = view.ActiveViewport.Size.Height
        view_capture.Width = int(self.tbox_width.Text)
        view_capture.Height = int(self.tbox_height.Text)
        view_capture.ScaleScreenItems = False
        view_capture.DrawAxes = False
        view_capture.DrawGrid = False
        view_capture.DrawGridAxes = False
        view_capture.TransparentBackground = False
        bitmap = view_capture.CaptureToBitmap(view)

        bitmap.Save(self.input_image_filename,
                    System.Drawing.Imaging.ImageFormat.Jpeg)

    def send_data(self):
        data = dict()
        data["session"] = self.session
        data["input_image"] = self.input_image_filename
        # r"C:\Users\szhang\github\EnneadTab-for-AI\output\working draft\imgs\IN\input.jpg"

        # <<<<>>>><<<<>>>> change this to the address of python<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        data["controlnet_model"] = "lllyasviel/sd-controlnet-canny"
        #data["controlnet_model"] = "L:\\4b_Applied Computing\\SD-Model\\sd-controlnet-canny"

        data["pipeline_model"] = MODEL_DICT.get(self.cb_model.SelectedIndex, None)
        if data["pipeline_model"] is None:
            NOTIFICATION.messenger(main_text="AI Model not selected!")
            
            return
        if self.cb_model.SelectedIndex != 0:
            data["pipeline_model"] = MODEL_FOLDER + \
                "\\" + data["pipeline_model"]
        print(data["pipeline_model"])

        data["positive_prompt"] = self.tbox_positive_prompts.Text
        data["negative_prompt"] = self.tbox_negative_prompts.Text
        data["number_of_output"] = int(self.tbox_num_of_img.Text)
        data["desired_resolution"] = [
            int(self.tbox_width.Text), int(self.tbox_height.Text)]
        data["iteration"] = int(self.tbox_iteration.Text)
        data["control_net_weight"] = self.weight_slider.Value/100.0

        if USER.IS_DEVELOPER:
            if self.foundation_pipeline_list.SelectedIndex == 0:
                data["foundation_pipeline"] = "control_net"
            elif self.foundation_pipeline_list.SelectedIndex == 1:
                data["foundation_pipeline"] = "img2img"
                # to be changed later
                data["reference_image"] = "C:\\Users\\szhang\\Desktop\\revit logo.png"
            elif self.foundation_pipeline_list.SelectedIndex == 2:
                data["foundation_pipeline"] = "in_paint"
                # to be changed later
                data["in_paint_mask_img"] = "C:\\Users\\szhang\\Desktop\\revit logo.png"

        data["direction"] = "IN"

        DATA_FILE.set_data(
            data, "AI_RENDER_DATA_{}.sexyDuck".format(TIME.get_formatted_current_time()))

        NOTIFICATION.messenger(main_text="Render Job Enqueued!")




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def view2render():
    # See if the form is already visible
    if sc.sticky.has_key('EA_AI_RENDER_CAPTURE_FORM'):
        print("form is already exisit")
        return

    # Create and show form
    form = ViewCaptureDialog()
    form.Owner = Rhino.UI.RhinoEtoApp.MainWindow
    form.Show()
    # Add the form to the sticky dictionary so it
    # survives when the main function ends.
    sc.sticky['EA_AI_RENDER_CAPTURE_FORM'] = form

    if USER.IS_DEVELOPER:
        is_testing_new_engine = False

        if is_testing_new_engine:
            return

    EXE.try_open_app("EA_AI_CONVERTER")



if __name__ == "__main__":
    view2render()