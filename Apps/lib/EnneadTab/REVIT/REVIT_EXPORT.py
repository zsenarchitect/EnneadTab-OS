#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)

import FOLDER
import IMAGE
import DATA_CONVERSION
import traceback
try:
    from Autodesk.Revit import DB # pyright: ignore

except :

    pass


def export_dwg(view_or_sheet, file_name, output_folder, dwg_setting_name, is_export_view_on_sheet = False):
    """   
    basic export funcs for DWG
    

    Args:
        view_or_sheet (DB.View | DB.ViewSheet): _description_
        file_name (str): file_name exclude .dwg at end
        output_folder (str of path): _description_
        dwg_setting_name (str): _description_
        is_export_view_on_sheet (bool, optional): _description_. Defaults to False.

    Returns:
        list: list of files exported
    """
    files_exported = []
    doc = view_or_sheet.Document

    if is_export_view_on_sheet and view_or_sheet.ViewType.ToString() == "DrawingSheet":
        view_ids = view_or_sheet.GetAllPlacedViews()
        #useful_sheet_count = 0
        for view_id in view_ids:
            view = doc.GetElement(view_id)

            if view.ViewType.ToString() in [ "Legend","Schedule", "Rendering"]:
                continue

            if "{3D" in view.Name:
                continue

            #useful_sheet_count += 1
            detail_num_para_id = DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
            detail_num = view.Parameter[detail_num_para_id].AsString() #get view detail num
            title_para_id = DB.BuiltInParameter.VIEW_DESCRIPTION
            title = view.Parameter[title_para_id].AsString() #get view title

            # prefix is that [2]_123_
            if len(file_name.split(view_or_sheet.SheetNumber)) == 1:
                prefix = ""
            else:
                prefix = file_name.split(view_or_sheet.SheetNumber)[0]

            view_file_name = "{}{}_{}_{}_[View On Sheet]".format(prefix, view_or_sheet.SheetNumber, detail_num, title)

            print ("Exporting view on sheet: {}.dwg".format(view_file_name))
            dwg_file = export_dwg(view, view_file_name, output_folder, dwg_setting_name, is_export_view_on_sheet)
            files_exported.extend(dwg_file)

    #DWG_export_setting = get_export_setting(doc, export_setting_name)
    DWG_option = DB.DWGExportOptions().GetPredefinedOptions(doc, dwg_setting_name)
    view_as_collection = DATA_CONVERSION.list_to_system_list([view_or_sheet.Id])
    max_attempt = 10
    attempt = 0
    while True:
        if attempt > max_attempt:
            print  ("Give up on <{}>, too many failed attempts, see reason above.".format(file_name))
            #global failed_export
            #failed_export.append(file_name)
            break
        attempt += 1
        try:
            doc.Export(output_folder, r"{}".format(file_name), view_as_collection, DWG_option)
            #print "DWG export succesfully: " + file_name
            break
        except Exception as e:
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                print("------**There is a file existing with same name, will attempt to save as {}**".format(file_name))

            else:
                print (e)
    FOLDER.cleanup_folder_by_extension(folder = output_folder, extension = ".pcp")
    files_exported.append(file_name + ".dwg")
    return files_exported



def export_image(view_or_sheet, file_name, output_folder, is_thumbnail = False, resolution = 6000, is_color_by_sheet = True):
    """basic exporter func for JPG

    Args:
        view_or_sheet (DB.View |DB.ViewSheet): _description_
        file_name (str): file_name exclude .jpg at end
        output_folder (str of path): _description_
        is_thumbnail (bool, optional): if true, set resolution to smaller jpg. This can override the resolution args. Defaults to False.
        resolution (int, optional): _description_. Defaults to 6000.

    Returns:
        str: final jpg name exported if successful, otherwise return False
    """
    
    doc = view_or_sheet.Document



    opts = DB.ImageExportOptions()
    try:
        opts.FilePath = output_folder + '\\{}.jpg'.format(file_name)
    except:
        print ("Error in export_image: {}".format(file_name))
        return False
    

        
    opts.ImageResolution = DB.ImageResolution.DPI_300
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.ZoomType = DB.ZoomFitType.FitToPage

    opts.PixelSize = 1200 if is_thumbnail else resolution

    opts.SetViewsAndSheets(DATA_CONVERSION.list_to_system_list([view_or_sheet.Id]))

    attempt = 0
    max_attempt = 5
    if os.path.exists(opts.FilePath):
        try:
            os.remove(opts.FilePath)
        except:
            pass
        
        
    while True:
        if attempt > max_attempt:
            print  ("Give up on <{}>, too many failed attempts, see reason above.".format(file_name))
            return False
            
        attempt += 1

        try:

            doc.ExportImage(opts)
            # print ("Image export succesfully")
            break
        except Exception as e:
            if  "The files already exist!" in str(e):
                file_name = file_name + "_same name"
                opts.FilePath = output_folder + '\\{}.jpg'.format(file_name)
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                print("------**There is a file existing with same name, will attempt to save as {}**".format(file_name))

            else:
                print( e.message)
    FOLDER.cleanup_name_in_folder(output_folder, file_name, ".jpg")

    if view_or_sheet.LookupParameter("Print_In_Color"):
        sheet_color_setting = view_or_sheet.LookupParameter("Print_In_Color").AsInteger()
    else:
        sheet_color_setting = 0

    if not is_color_by_sheet:
        sheet_color_setting = 0
    if sheet_color_setting:
        file_path = "{}\\{}.jpg".format(output_folder, file_name)
        bw_file = "{}\\{}_BW.jpg".format(output_folder, file_name)
        IMAGE.convert_image_to_greyscale(file_path, bw_file)
        try:
            os.remove(file_path)
            os.rename(bw_file, file_path)
        except:
            pass
        
    return file_name + ".jpg"
