#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Attempt to export the same axon view from archive files"
__title__ = "Export GIF From Archive Model"

from pyrevit import forms #
from pyrevit import script #
import time
import os


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def export_image_from_view(view, doc):

    print("-----")


    time_start = time.time()

    file_name = view.Name

    print("preparing [{}].jpg".format(file_name))

    output_folder = "{}\Documents\{}".format(os.environ["USERPROFILE"], "###Axon Views Jpgs for [{}]".format(doc.Title))

    #dir = os.path.join("C:\\","temp","python")
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)


    opts = DB.ImageExportOptions()
    opts.FilePath = output_folder + r'\{}.jpg'.format(file_name)
    opts.ImageResolution = DB.ImageResolution.DPI_300
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 6000
    opts.SetViewsAndSheets(EnneadTab.DATA_CONVERSION.list_to_system_list([view.Id]))

    attempt = 0

    while True:
        if attempt > 0:
            break
        try:
            doc.ExportImage(opts)
            print("Image export succesfully")
            break
        except Exception as e:
            attempt += 1
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                output.print_md("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

            else:
                print("failed export view [{}] becasue: {}".format(view.Name, e))
                return
    time_end = time.time()
    #cleanup_jpg_name()
    print("view to Jpg takes {} seconds".format( time_end - time_start))
    cleanup_jpg_name(output_folder, file_name, str(view.ViewType))
    #add_to_log(file_name + ".jpg", time_end - time_start)
    EA_UTILITY.show_toast(app_name = "EnneadTab Exporter",
                            title = "[{}.jpg] saved.".format(file_name),
                            message = "{} more to do in current document".format(total - counter))


def process_file(file, camera, ref_view_name):

    model_path = DB.ModelPathUtils.ConvertUserVisiblePathToModelPath(file)
    open_options = DB.OpenOptions()

    open_options.DetachFromCentralOption = DB.DetachFromCentralOption.DetachAndPreserveWorksets

    try:
        new_doc = EnneadTab.REVIT.REVIT_APPLICATION.get_application().OpenDocumentFile(model_path,open_options)

        views = DB.FilteredElementCollector(new_doc).OfClass(DB.View3D).WhereElementIsNotElementType().ToElements()
        views = filter(lambda x: x.Name == ref_view_name, views)
        if len(views) != 0:
            view = views[0]
            t = DB.Transaction(new_doc, "set cam")
            t.Start()
            view.SetOrientation = camera
            export_image_from_view(view, new_doc)
            t.RollBack()
    except Exception as e:
        print (e)
    finally:
        new_doc.Close(False)

def export_gif_from_archive():
    pass

    # get current axon camera position, have to a 3D view
    view = doc.ActiveView
    ref_view_name = view.Name
    if view.ViewType.ToString() != "ThreeD":
        print("Can ony do 3D view")
        return
    camera = view.GetOrientation

    # get a list of  files to detach, use short cut. short cut name  is date.
    files = list(forms.pick_file(file_ext = "rvt", multi_file=True, title = "Pick the shortcut to your revit archive."))

    print(files)

    # process shortcut, open with detach,
    map(lambda x: process_file(x, camera, ref_view_name), files)



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    export_gif_from_archive()
    



