
__title__ = "ExtractPreviewImages"
__doc__ = "This button does ExtractPreviewImages when left click"

import rhinoscriptsyntax as rs
import scriptcontext as sc
import os.path as op
import os
import System # pyright: ignore


def extract_preview_images():

    

    main_folder = "L:\\4b_Applied Computing\\00_Asset Library"
    file_paths = ["{}\{}".format(main_folder,x) for x in os.listdir(main_folder) if ".3dm" in x[-4:].lower()]
   
    target_folder = "L:\\4b_Applied Computing\\00_Asset Library\\Database\\data"

    total_count = len(file_paths)
    LOG = ""
    for i, file_path in enumerate(file_paths):
        #print file_path
        i += 1
        try:
            head, tail = op.split(file_path)
            jpg_name = tail.replace(".3dm", ".png")
            jpg_name = "{}\{}".format(target_folder, jpg_name)

            image = sc.doc.ExtractPreviewImage (file_path)

            image.Save(jpg_name, System.Drawing.Imaging.ImageFormat.Png)
            print("Getting {}/{} png as {}".format(i + 1, total_count, jpg_name))
        except Exception as e:
            note = "Failed {}/{} png as {} becasue {}".format(i + 1, total_count, file_path, e)
            print(note)
            LOG += "\n{}".format(note)

    if len(LOG) != 0:
        rs.TextOut(LOG)
