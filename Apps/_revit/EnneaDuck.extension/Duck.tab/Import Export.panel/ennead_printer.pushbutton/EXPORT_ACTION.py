import time


from EnneadTab import NOTIFICATION
from EnneadTab import FOLDER
from Autodesk.Revit import DB # pyright: ignore #pylint: disable=undefined-variable
from pyrevit import script
import os

from EnneadTab import IMAGES

# import ennead_printer_script as ENNEAD_PRINTER_SCRIPT
#
# host_window = ENNEAD_PRINTER_SCRIPT.window
def print_time(title, time_end, time_start, use_minutes = False):
    output = script.get_output()
    if not use_minutes:
        foot_note = "{} seconds".format( time_end - time_start)
        output.print_md("{} takes **{}** seconds".format(title, time_end - time_start))
        return foot_note
    mins = int((time_end - time_start)/60)
    output.print_md("{} takes **{}** mins".format(title, mins))
    foot_note = "{} mins".format( mins)
    return foot_note


def get_print_setting(doc, is_color_by_sheet, is_color = True, is_A1_paper = True):


    all_print_settings = DB.FilteredElementCollector(doc).OfClass(DB.PrintSetting)

    if is_color_by_sheet:
        is_color = False

    if is_color:
        all_print_settings = filter(lambda x: "COLOR" in x.Name, all_print_settings)
    else:
        all_print_settings = filter(lambda x: "GRAYSCALE" in x.Name, all_print_settings)

    if is_A1_paper:
        all_print_settings = filter(lambda x: "A1" in x.Name, all_print_settings)
    else:
        all_print_settings = filter(lambda x: "A0" in x.Name, all_print_settings)

    #print all_print_settings[0].Name
    if len(all_print_settings) > 0:
        return all_print_settings[0]
    print ("!!!Cannot find print setting that has 'COLOR/GRAYSCALE' or 'A1/A0' in it. Use default")
    return DB.FilteredElementCollector(doc).OfClass(DB.PrintSetting).FirstElement()



"""
                   _                                          _
 _ __ ___    __ _ (_) _ __     ___ __  __ _ __    ___   _ __ | |_
| '_ ` _ \  / _` || || '_ \   / _ \\ \/ /| '_ \  / _ \ | '__|| __|
| | | | | || (_| || || | | | |  __/ >  < | |_) || (_) || |   | |_
|_| |_| |_| \__,_||_||_| |_|  \___|/_/\_\| .__/  \___/ |_|    \__|
                                         |_|
"""


def export_image(view_or_sheet, file_name, output_folder, is_thumbnail = False, is_color_by_sheet = True):
    """
    file_name exclude .jpg at end
    """
    doc = view_or_sheet.Document



    opts = DB.ImageExportOptions()
    opts.FilePath = output_folder + r'\{}.jpg'.format(file_name)
    if os.path.exists(opts.FilePath):
        try:
            os.remove(opts.FilePath)
        except:
            pass

    
    opts.ImageResolution = DB.ImageResolution.DPI_300
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.ZoomType = DB.ZoomFitType.FitToPage

    opts.PixelSize = 6000
    if is_thumbnail:
        opts.PixelSize = 1200

    opts.SetViewsAndSheets(EA_UTILITY.list_to_system_list([view_or_sheet.Id]))

    attempt = 0
    max_attempt = 10

    while True:
        if attempt > max_attempt:
            print  ("Give up on <{}>, too many failed attempts, see reason above.".format(file_name))
            return False
            break
        attempt += 1

        try:

            doc.ExportImage(opts)
            print ("Image export succesfully")
            break
        except Exception as e:
            if  "The files already exist!" in str(e):
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                print("------**There is a file existing with same name, will attempt to save as {}**".format(file_name))

            else:
                print (e.message)
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
        IMAGES.convert_image_to_greyscale(file_path, bw_file)

        try:
            os.remove(file_path)
            os.rename(bw_file, file_path)
        except:
            pass
    return file_name + ".jpg"

def export_dwg(view_or_sheet, file_name, output_folder, dwg_setting_name, is_export_view_on_sheet):
    """
    file_name exclude .dwg at end
    """
    
    if "*" in view_or_sheet.Name:
        NOTIFICATION.messenger(main_text="<{}> contains * in name. Please fix!".format(view_or_sheet.Name))
        return []
    if hasattr(view_or_sheet, "SheetNumber") and "*" in view_or_sheet.SheetNumber:
        NOTIFICATION.messenger(main_text="<{}> contains * in sheet number. Please fix!".format(view_or_sheet.SheetNumber))
        return []
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
    view_as_collection = EA_UTILITY.list_to_system_list([view_or_sheet.Id])
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
    EA_UTILITY.cleanup_folder(folder = output_folder, extension = ".pcp")
    files_exported.append(file_name + ".dwg")
    return files_exported


def export_pdf(view_or_sheet, file_name, output_folder, is_color_by_sheet):
    """
    file_name exclude .pdf at end
    """
    doc = view_or_sheet.Document


    def override_blue_lines():
        pass

    def dry_transaction_decorator(f):
        def warper():
            t = DB.Transaction(doc, "dry T")
            t.Start()
            f()
            t.RollBack()
        return warper



    def pdf_method_1():
        #  ----- method 1 -----
        print ("$$$ Trying method 1")
        t = DB.Transaction(doc, "temp")
        t.Start()


        titleBlock = DB.FilteredElementCollector(doc, view_or_sheet.Id).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).FirstElement()
        #print titleBlock.Symbol.Family.Name


        print_manager = doc.PrintManager
        print_manager.PrintToFile = True
        #print_manager.IsVirtual = True
        print_manager.SelectNewPrintDriver("Bluebeam PDF")
        # print_manager.Apply()

        if view_or_sheet.LookupParameter("Print_In_Color"):
            sheet_use_color = view_or_sheet.LookupParameter("Print_In_Color").AsInteger()
        else:
            sheet_use_color = 0
            print ("Cannot find 'Print_In_Color' in sheet para...Use NO color as default.")
        print_manager.PrintSetup.CurrentPrintSetting = get_print_setting(doc,
                                                                        is_color_by_sheet,
                                                                        is_color = sheet_use_color,
                                                                        is_A1_paper = "A1" in titleBlock.Symbol.Family.Name)
        # print_manager.Apply()
        #t.Commit()
        #"""
        print ("Print Setting Name = [{}]".format(print_manager.PrintSetup.CurrentPrintSetting.Name))
        print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
        print_manager.PrintRange = DB.PrintRange.Select
        view_set = DB.ViewSet()
        view_set.Insert(view_or_sheet)
        try:
            print_manager.ViewSheetSetting.InSession.Views = view_set
        except:
            print ("InSession ViewSheetSet failed, trying with CurrentViewSheetSet...")
            print_manager.ViewSheetSetting.CurrentViewSheetSet.Views = view_set
        # print_manager.Apply()
        # t.Commit()
        #print print_manager.PrintToFileName

        """might be important again"""
        #reactivate_output()

        while True:
            try:
                try:
                    print_manager.SubmitPrint(view_or_sheet)
                except:
                    print ("2nd method")
                    print_manager.SubmitPrint()
                print ("PDF export succesfully")
                break
            except Exception as e:
                if  "The files already exist!" in e:
                    raw_name = file_name + "_same name"
                    new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                    print ("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

                elif "no views/sheets selected" in e:
                    print (e)
                    print ("...")
                    print (print_manager.PrintToFileName)
                    print ("problem sheet = {}".format(view_or_sheet.Name))
                    has_non_print_sheet = True
                else:
                    print (e)
                    print (print_manager.PrintToFileName)
                    print ("problem sheet = {}".format(view_or_sheet.Name))
                break

        t.RollBack()
        #print t.GetStatus()

        """might be important again"""
        #cleanup_pdf_name()
        FOLDER.cleanup_name_in_folder(output_folder, file_name, ".pdf")

        print ("$$$ end method 1")

    def pdf_method_2():
        #  ----- method 2 -----
        #print "$$$ Trying method 2"

        sheet_list = EA_UTILITY.list_to_system_list([view_or_sheet.Id])


        pdf_options = DB.PDFExportOptions ()
        pdf_options.Combine = False



        name_rule = pdf_options.GetNamingRule ()
        #print name_rule

        sheet_num_para_data = DB.TableCellCombinedParameterData.Create()
        sheet_num_para_data.ParamId = DB.ElementId(DB.BuiltInParameter.SHEET_NUMBER)
        if len(file_name.split(view_or_sheet.SheetNumber)) == 1:
            sheet_num_para_data.Prefix = ""
        else:
            sheet_num_para_data.Prefix = file_name.split(view_or_sheet.SheetNumber)[0]
        sheet_num_para_data.Separator = " - "

        sheet_name_para_data = DB.TableCellCombinedParameterData.Create()
        sheet_name_para_data.ParamId = DB.ElementId(DB.BuiltInParameter.SHEET_NAME)

        # IList<TableCellCombinedParameterData> GetNamingRule()
        new_rule = [sheet_num_para_data, sheet_name_para_data]
        new_rule = EA_UTILITY.list_to_system_list(new_rule, type = "TableCellCombinedParameterData", use_IList = False)
        pdf_options.SetNamingRule(new_rule)

        if view_or_sheet.LookupParameter("Print_In_Color"):
            sheet_color_setting = view_or_sheet.LookupParameter("Print_In_Color").AsInteger()
        else:
            sheet_color_setting = 0

        if not is_color_by_sheet:
            sheet_color_setting = 0
        if sheet_color_setting:
            pdf_options.ColorDepth = DB.ColorDepthType.Color
        else:
            pdf_options.ColorDepth = DB.ColorDepthType.GrayScale

        #pdf_options.ExportPaperFormat = DB.ExportPaperFormat.Default


        doc.Export(output_folder, sheet_list, pdf_options)
        #print "$$$ end method 2"


    pdf_method_2()
    return file_name + ".pdf"




"""
after export
"""

def combine_final_pdf(output_folder, files_exported_for_this_issue, combined_pdf_name, copy_folder = None):
    """files_exported_for_this_issue --> list of file name with extension
    """
    import os
    list_of_filepaths = []
    files = EA_UTILITY.get_filenames_in_folder(output_folder)

    for file in files:
        if ".pdf" not in file.lower():
            continue

        if file in files_exported_for_this_issue:
            file_path = os.path.join(output_folder, file)
            print ("--combining PDF: {}".format(file_path))
            list_of_filepaths.append(file_path)

    combined_pdf_file_path = "{}\{}.pdf".format(output_folder, combined_pdf_name)
    EA_UTILITY.merge_pdfs(combined_pdf_file_path, list_of_filepaths, reorder = True)
    if copy_folder:
        EA_UTILITY.copy_file_to_folder(combined_pdf_file_path, copy_folder)



def dump_exported_files_to_copy_folder(output_folder, files_exported_for_this_issue, file_id_dict, copy_folder):

    import os.path as op

    for file in EA_UTILITY.get_filenames_in_folder(output_folder):
        if file in files_exported_for_this_issue:
            file_path = op.join(output_folder, file)


            try:
                plot_id = file_id_dict[file]
            except:
                plot_id = "Missing"



            if ".pdf" in file.lower():
                if plot_id:
                    new_folder = "{}\{}\PDFs".format(copy_folder, plot_id)
                else:
                    new_folder = "{}\PDFs".format(copy_folder)
                new_folder = EA_UTILITY.secure_folder(new_folder)

            elif ".dwg" in file.lower():
                if plot_id:
                    new_folder = "{}\{}\DWGs".format(copy_folder, plot_id)
                else:
                    new_folder = "{}\DWGs".format(copy_folder)
                new_folder = EA_UTILITY.secure_folder(new_folder)

            elif ".jpg" in file.lower():
                if plot_id:
                    new_folder = "{}\{}\JPGs".format(copy_folder, plot_id)
                else:
                    new_folder = "{}\JPGs".format(copy_folder)
                new_folder = EA_UTILITY.secure_folder(new_folder)

            else:
                new_folder = copy_folder[:]

            EA_UTILITY.copy_file_to_folder(file_path, new_folder)




def create_print_in_color_para(doc):
    pass







if __name__ == "__main__":
    pass