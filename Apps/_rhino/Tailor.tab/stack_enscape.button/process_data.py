import os
import win32com.client
import sys
sys.path.append(r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\lib")
# from Duckitect import NOTIFICATION
import time

import prepare_data

class BlendMode:
    Screen = 9
    Lighten = 8
    Pass = 0
    
class Stacker:
    psapp = win32com.client.Dispatch("Photoshop.Application")


    
    def __init__(self, study):
        print ("\n\nWorking on study <{}>".format(study))
        self.study = study
        self.collection_pairs = prepare_data.get_collection_pairs(study)



    def process_PSD(self):
        if not self.collection_pairs:
            print ("cannot find valid images to stack")
            return

        # note do not use map becasue py3 map is diff from py2
        # self.collection_pairs = self.collection_pairs[::-1]
        total = len(self.collection_pairs)
        for i, pair in enumerate(self.collection_pairs):
            print ("{}/{}...".format(i+1, total))
            self.process_file(pair)
        

    def process_file(self, file_pair):
        glass_version, chrome_version = file_pair
        root_folder = os.path.dirname(os.path.dirname(glass_version))
        view_name = glass_version.split("_")[-1].split(".")[0]
        print ("Working on <{}>".format(view_name))

        

        if "cam 13" in view_name.lower():
            Stacker.psapp.Open(r"J:\1643\1_Presentation\01_P-Base\01_Base Renderings\archive\CITY.png")
            doc = Stacker.psapp.Application.ActiveDocument
            layer = doc.ArtLayers[0]
            layer.name = "city"
            self.add_img_as_layer(doc,
                                  glass_version, 
                                  "glass_version",
                                  change_color_blend=False)

        elif "cam 17" in view_name.lower():
            Stacker.psapp.Open(r"J:\1643\1_Presentation\01_P-Base\01_Base Renderings\archive\CAM17.png")
            doc = Stacker.psapp.Application.ActiveDocument
            layer = doc.ArtLayers[0]
            layer.name = "patient room bg"
            self.add_img_as_layer(doc,
                                  glass_version, 
                                  "glass_version",
                                  change_color_blend=False)
            self.add_img_as_layer(doc,
                                  glass_version, 
                                  "overlayer",
                                  change_color_blend=BlendMode.Screen,
                                  blend_strength=20)
            
        else:
            Stacker.psapp.Open(glass_version)
            doc = Stacker.psapp.Application.ActiveDocument

            
            layer = doc.ArtLayers[0]
            layer.name = "glass_version"
        
        PSD_path = "{}\\temp.psd".format(root_folder)
        doc.SaveAs(PSD_path)
        
        self.add_img_as_layer(doc, chrome_version, "chrome_version")

        # adjust brifhtness for noth view
        if "elevation north" in view_name.lower():
            pass
            #self.add_brightness_adjustment_layer(doc, glass_version)

        # After processing, add the "Work in progress" text
        WIP_studys = []
        wip = r"J:\1643\1_Presentation\01_P-Base\01_Base Renderings\archive\WIP.png"
        if self.study in WIP_studys:
            self.add_img_as_layer(doc, wip, "wip", is_text_anno = True)

        PSD_path = "{}\psd\{}_{}.psd".format(root_folder, self.study, view_name)
        doc.SaveAs(PSD_path) # make it psd file first so other png can open again and copy if same name. this is to handle the case where no pair is ffound.
        JPG_path = "{}\{}_{}.jpg".format(root_folder, self.study, view_name)
        # print(PSD_path)

        # Save as JPG
        jpgSaveOptions = win32com.client.Dispatch("Photoshop.JPEGSaveOptions")
        jpgSaveOptions.EmbedColorProfile = True
        jpgSaveOptions.FormatOptions = 2  # Standard Baseline
        jpgSaveOptions.Matte = 1  # None
        jpgSaveOptions.Quality = 12  # Maximum Quality
        doc.SaveAs(JPG_path, jpgSaveOptions, True)
        doc.Close(2)  # Close the document without saving changes

    def get_extension(self, file_path):
        _, extension = os.path.splitext(file_path)
        return extension

    @staticmethod
    def get_file_name(file_path):
        return os.path.basename(file_path).split(".")[0]


    def add_brightness_adjustment_layer(self, current_doc, src_file):
        print (" - Adding a brightener")
        Stacker.psapp.Load(src_file)
        Stacker.psapp.ActiveDocument.Selection.SelectAll()
        Stacker.psapp.ActiveDocument.Selection.Copy()
        Stacker.psapp.ActiveDocument.Close()



        current_doc.ArtLayers.Add()

        # Paste and get reference to the new layer
        current_doc.Paste()
        new_layer = current_doc.ActiveLayer
        new_layer.name = "brightener"

        new_layer.BlendMode = 9 # use screen
        new_layer.Opacity = 20
            
    def add_img_as_layer(self, current_doc, file_path, layer_name, is_text_anno = False, change_color_blend = BlendMode.Lighten, blend_strength = 40):
        if not os.path.exists(file_path):
            print (" - There is no chrome version found.")
            return

        Stacker.psapp.Load(file_path)
        Stacker.psapp.ActiveDocument.Selection.SelectAll()
        Stacker.psapp.ActiveDocument.Selection.Copy()
        Stacker.psapp.ActiveDocument.Close()

        # for i,item in enumerate(dir(Stacker.psapp.ActiveDocument.ActiveLayer.BlendMode)):
        #     print (i, item)

        current_doc.ArtLayers.Add()

        # Paste and get reference to the new layer
        current_doc.Paste()
        new_layer = current_doc.ActiveLayer
        new_layer.name = layer_name

        if is_text_anno:
            print("  - Stack WIP text on new layer.")
            return
        else:
            print("  - Stack image on new layer.")


        if not change_color_blend:
            return
        # Attempt to set blend mode to Lighten
        try:
            # If the named constant does not work, use the numerical value for Lighten blend mode
            # print ("current mode = {}".format(new_layer.BlendMode))
            new_layer.BlendMode = change_color_blend # 8 is the Lighten mode
            print("  - Setting new layer color blend mode to \"{}\"".format(str(change_color_blend)))
            # new_layer.BlendMode = win32com.client.Dispatch("Photoshop.BlendMode.BlendMode.LIGHTEN")
        except Exception as e:
            # Fallback: Use a numerical value directly if the above fails
            # The numerical value needs to be determined based on Photoshop documentation or testing
            # For example, if Lighten corresponds to a value of 2 (this is just an example, not the actual value)
            # new_layer.BlendMode = 2
            print(e)

        new_layer.Opacity = blend_strength
        print("  - Setting new layer opacity to {}%".format(int(new_layer.Opacity))) 

def main():
    studys = ["simple_punch",
        # "offset_frame",
        # "hori",
        # "angled_frame", #precast bg, copper foreground
        # "angled_frame_alt", #copper on bg and fg
        # "angled_frame_alt_alt", #terraceoota on bg and fg
        # "sawtooth",
        # "solar_panel", 
              ]
    start_time = time.time()        
    for study in studys:
        stacker = Stacker(study)
        stacker.process_PSD()
    # NOTIFICATION.messenger("All images processed")
    Stacker.psapp.Quit()

    time_diff = time.time() - start_time

    print ("\n\nAll processed in {}s!!".format(int(time_diff)))


if __name__ == "__main__":
    # wait 1 hour then start
    # time.sleep(3600)
    main()