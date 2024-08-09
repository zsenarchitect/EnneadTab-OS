__doc__ = "The original flavour auto-exporter. It export pdf and dwgs and jpg, package them to different folders, and control the print by issuing parameter. The paper size and color setting is picked automatically by sheets parameter."
__title__ = "19_[PDF and DWG and JPG exporter] <------"


"""
improvement list::
------done:  setup testing issue seting in dropdown menu to quicjktest
-----fixed: after one succesfully run, the second run will not work for primay doc printing
----done:detect output folder to warn that there are pdf and dwg already
----done: try 03 of 22 sheet.
------done:   try print using color para,!!!!!!!
----done: try print pdf based on titleblock size!!!!!
try format print log report as table, also sort it. pretty table....
try sending email after done, no module install...show printing time in text body.
------done:   try define output folder as user folder
----done: try close docs after all printed as option. need a placeholder doc in the bundle file path to replace the actual doc so you can close

can wrap all post export action (email, save log, close primary doc) as selection list multiuple option
"""



from pyrevit import forms, DB, revit, script
import os
import os.path as op
import time
import System
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()


def legalize_filename(name):
    if r"/" in name:
        print("Windows file name cannot contain '/' in its name, i will replace it with '-'")
    return name.replace("/", "-")

def reactivate_output():
    output = script.get_output()

def add_to_log(file, time):

    global main_log
    main_log.append((time, file))

def remove_extra_dot():
    file_names = os.listdir(fix_folder)
    for file_name in file_names:
        if "..pdf" in file_name.lower():
            try:
                os.rename(op.join(fix_folder, file_name),op.join(fix_folder, file_name.replace("..", ".")))
            except:
                print("skip {}".format(file_name))


def delete_extra_file(basefolder, key_ext):
    filenames = os.listdir(basefolder)
    PCP_file_found = False
    count = 0
    for current_file in filenames:
        ext = op.splitext(current_file)[1].upper()
        if ext == key_ext:
            try:
                os.remove(op.join(basefolder, current_file))
                count += 1
            except Exception as e:
                EA_UTILITY.print_note("Cannot delete file [{}] becasue error: {}".format(current_file, e))
    return count


def cleanup_jpg_name():


    keyword = " - Sheet - "
    file_names = os.listdir(output_folder)

    for file_name in file_names:
        if keyword in file_name and ".jpg" in file_name.lower():
            new_name = file_name.split(keyword)[0]

            try:
                os.rename(op.join(output_folder, file_name),op.join(output_folder, new_name + ".jpg"))
            except:
                print("skip {}".format(file_name))

def cleanup_pdf_name():

    delete_extra_file(output_folder,".PCP")
    delete_extra_file(output_folder,".PS")

    keyword = "- Sheet - "
    file_names = os.listdir(output_folder)

    for file_name in file_names:
        if keyword in file_name and ".pdf" in file_name.lower():
            new_name = file_name.split(keyword)[1]
            if has_index:
                sheet_number = new_name.split(" - ")[0]
                try:
                    new_name = index_dict[sheet_number] + "_" + new_name
                except KeyError:
                    output.print_md( "##in the folder there are sheets exported from your other issue parameter, so the indexing could be mixed. this is dangerous, please ask Sen for details.")

            try:
                os.rename(op.join(output_folder, file_name),op.join(output_folder, new_name))
            except:
                print("skip renaming {} due to ownership".format(file_name))


def print_time(title, time_end, time_start, use_minutes = False):
    if not use_minutes:
        output.print_md("{} takes **{}** seconds".format(title, time_end - time_start))
        return
    mins = int((time_end - time_start)/60)
    output.print_md("{} takes **{}** mins".format(title, mins))

def get_issue_date_info(doc):
    info = DB.FilteredElementCollector(doc).OfClass(DB.ProjectInfo).FirstElement()
    return info.LookupParameter("Sheet Issue Date by Project").AsString()
    # date_paras = DB.ProjectInfo.GetParameters("Project Issue Date")
    # for para in date_paras:
    #     print para.AsString()
    # return para.AsString()


def show_setting_helper():
    output.print_md( "open your **bluebeam administrator**(not the bluebeam viewer)")
    print("on the printer tab, \n\t-disable 'prompt for file name'\n\t-disable 'open in viewer\n\t-Set default output folder as ('User/Documents') in 'folder option'\n\nShould look like this below.")
    img_path = script.get_bundle_file("bluebeam admin setting.png")
    output.set_height(1000)
    output.print_image(img_path)





def close_docs_by_name(names = [], close_all = False):

    def safe_close(doc):
        name = doc.Title
        doc.Close(False)
        doc.Dispose()#########################
        print("{} closed".format(name))

    docs = get_top_revit_docs()
    if close_all:
        map(safe_close, docs)
        return

    for doc in docs:
        if doc.Title in names:
            try:
                safe_close(doc)
            except Exception as e:
                print (e)
                print("skip closing [{}]".format(doc.Title))


def get_top_revit_docs():

    docs = app.Documents
    EA_UTILITY.print_note("1/2, cuurent every docs in application, including links and family doc = {}".format(str([x.Title for x in docs])))
    OUT = []
    for doc in docs:
        if doc.IsLinked or doc.IsFamilyDocument:
            continue
        OUT.append(doc)
    EA_UTILITY.print_note("2/2, cuurent every docs in application, without link and family doc = {}".format(str([x.Title for x in OUT])))
    return OUT


def active_original_doc(doc_name):
    from Autodesk.Revit import UI # pyright: ignore
    for data in GUID_list:
        if data[0] == doc_name:
            break

    cloud_path = DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(System.Guid(data[1]), System.Guid(data[2]) )
    open_options = DB.OpenOptions()
    EA_UTILITY.print_note( "setting active doc as {}".format(data[0]))
    return UI.UIApplication(app).OpenAndActivateDocument (cloud_path,
                                                        open_options,
                                                        False)


def open_doc_in_background(doc_name):
    for data in GUID_list:
        if data[0] == doc_name:
            break

    cloud_path = DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(System.Guid(data[1]), System.Guid(data[2]) )
    open_options = DB.OpenOptions()
    new_doc = app.OpenDocumentFile(cloud_path,
                                open_options)

    #output.print_md( "background open file {}".format(doc_name))





def get_export_setting(doc, setting_name = "Empty"):
    existing_dwg_settings = DB.FilteredElementCollector(doc)\
                                .OfClass(DB.ExportDWGSettings)\
                                .WhereElementIsNotElementType()\
                                .ToElements()


    def pick_from_setting():
        sel_setting = None
        attempt = 0
        while sel_setting == None:
            if attempt > 3:
                break
            sel_setting = forms.SelectFromList.show(existing_dwg_settings, \
                                                    name_attr = "Name", \
                                                    button_name='always use setting with this name for this export job', \
                                                    title = "Select existing Export Setting.")
            if sel_setting == None:
                EA_UTILITY.dialogue(main_text = "You didn't select any export setting. Try again.")
                attempt += 1
            else:
                break

        return sel_setting



    if setting_name == "Empty":##trying to defin the setting for the first time
        sel_setting = pick_from_setting()

    else:####trying to match a setting name from input
        sel_setting = None
        for setting in existing_dwg_settings:
            if setting.Name == setting_name:
                sel_setting = setting
                break
        if sel_setting == None:
            EA_UTILITY.dialogue(main_text = "Cannot find setting with same name to match [{}], please manual select".format(setting_name))
            sel_setting = pick_from_setting()


    return sel_setting


def get_print_setting(doc, is_color = True, is_A1_paper = True):


    all_print_settings = DB.FilteredElementCollector(doc).OfClass(DB.PrintSetting)
    global FORCE_BW_PDF
    if FORCE_BW_PDF:
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
    return all_print_settings[0]



    """
    print_parameters = print_setting.PrintParameters

    if is_color:
        print ("use color")
        print_parameters.ColorDepth = DB.ColorDepthType.Color
        print(print_parameters.ColorDepth)
    else:
        print("use grayscale")
        print_parameters.ColorDepth = DB.ColorDepthType.GrayScale
        print(print_parameters.ColorDepth)
    return

    if is_A1_paper:
        print_parameters.PaperSize = "ISO_A1_(594.00_x_841.00_MM)"
    else:
        print_parameters.PaperSize = "ISO_A0_(841.00_x_1189.00_MM)"
    """


def export_image_from_sheet(sheet, doc):
    print("-----")
    time_start = time.time()

    file_name = "{} - {}".format(sheet.SheetNumber, sheet.Name)
    if has_index:
        file_name = index_dict[sheet.SheetNumber] + "_" + file_name

    file_name = legalize_filename(file_name)
    print("preparing [{}].jpg".format(file_name))
    EA_UTILITY.remove_exisitng_file_in_folder(output_folder, file_name + ".jpg")

    opts = DB.ImageExportOptions()
    opts.FilePath = output_folder + r'\{}.jpg'.format(file_name)
    opts.ImageResolution = DB.ImageResolution.DPI_300
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 6000
    opts.SetViewsAndSheets(EA_UTILITY.list_to_system_list([sheet.Id]))

    attempt = 0
    max_attempt = 10
    while True:
        if attempt > max_attempt:
            print("Give up on <{}>, too many failed attempts, see reason above.".format(file_name))
            global failed_export
            failed_export.append(file_name)
            break
        attempt += 1

        try:
            doc.ExportImage(opts)
            print("Image export succesfully")
            break
        except Exception as e:
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                output.print_md("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

            else:
                print (e)
    time_end = time.time()
    cleanup_jpg_name()
    print_time("sheet to Jpg", time_end, time_start)
    add_to_log(file_name + ".jpg", time_end - time_start)
    EA_UTILITY.show_toast(app_name = "Bilibili exporter",
                            title = "[{}.jpg] saved.".format(file_name),
                            image = "C:\Users\szhang\github\EnneadTab 2.0\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135.pulldown\icon.png",
                            message = "{} more to do in current document".format(total - counter))

def export_views_on_sheet(sheet, doc):
    print("--------try to export views on sheet first:")
    view_ids = sheet.GetAllPlacedViews()
    useful_sheet_count = 0
    for view_id in view_ids:
        view = doc.GetElement(view_id)

        if view.ViewType.ToString() == "Legend":
            continue
        if view.ViewType.ToString() == "Schedule":
            continue
        if "{3D" in view.Name:
            continue

        useful_sheet_count += 1
        detail_num_para_id = DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
        detail_num = view.Parameter[detail_num_para_id].AsString() #get view detail num
        title_para_id = DB.BuiltInParameter.VIEW_DESCRIPTION
        title = view.Parameter[title_para_id].AsString() #get view title

        file_name = "{}_{}_{}__[View On Sheet]".format(sheet.SheetNumber, detail_num, title)
        if has_index:
            file_name = index_dict[sheet.SheetNumber] + "_" + file_name
        export_dwg_action(file_name, view, doc)
    if useful_sheet_count == 0:
        print("no exportable viewport found on this sheet.")

def export_dwg_action(file_name, view_or_sheet, doc, additional_msg = ""):
    time_start = time.time()
    file_name = legalize_filename(file_name)
    if r"/" in file_name:
        file_name = file_name.replace("/", "-")
        print("Windows file name cannot contain '/' in its name, i will replace it with '-'")
    print("preparing [{}].dwg".format(file_name))
    EA_UTILITY.remove_exisitng_file_in_folder(output_folder, file_name + ".dwg")
    view_as_collection = System.Collections.Generic.List[DB.ElementId]([view_or_sheet.Id])
    max_attempt = 10
    attempt = 0
    while True:
        if attempt > max_attempt:
            print("Give up on <{}>, too many failed attempts, see reason above.".format(file_name))
            global failed_export
            failed_export.append(file_name)
            break
        attempt += 1
        try:
            doc.Export(output_folder, r"{}".format(file_name), view_as_collection, DWG_option)
            print("DWG export succesfully")
            break
        except Exception as e:
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                output.print_md("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

            else:
                if "no views/sheets selected" in e:
                    print (e)
                    print("000000000")
                    has_non_print_sheet = True
                else:

                    print (e)

    time_end = time.time()
    print_time("exporting DWG", time_end, time_start)
    add_to_log(file_name + ".dwg", time_end - time_start)

    EA_UTILITY.show_toast(app_name = "Bilibili exporter",
                            title = "[{}.dwg] saved.".format(file_name),
                            image = "C:\Users\szhang\github\EnneadTab 2.0\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135.pulldown\icon.png",
                            message = additional_msg)



def export_DWG_from_sheet(sheet, doc):
    print("-----")

    if is_export_view_on_sheet:
        try:
            export_views_on_sheet(sheet, doc)
        except Exception as e:
            print("Something is not right, let Sen know. Error = {}".format(e))


    time_start = time.time()
    print("--------try to export sheet:")
    file_name = "{} - {}".format(sheet.SheetNumber, sheet.Name)
    if has_index:
        file_name = index_dict[sheet.SheetNumber] + "_" + file_name

    export_dwg_action(file_name, sheet, doc, additional_msg = "{} more to do in current document".format(total - counter))
    return
    """
    print("preparing [{}].dwg".format(file_name))
    EA_UTILITY.remove_exisitng_file_in_folder(output_folder, file_name + ".dwg")

    #print_manager.PrintToFileName = r"{}\{}.dwg".format(output_folder, file_name)
    #print print_manager.PrintToFileName


    sheet_as_collection = System.Collections.Generic.List[DB.ElementId]([sheet.Id])



    while True:
        try:
            doc.Export(output_folder, file_name, sheet_as_collection, DWG_option)
            print("DWG export succesfully")
            break
        except Exception as e:
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                output.print_md("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

            else:
                if "no views/sheets selected" in e:
                    print (e)
                    print("000000000")
                    has_non_print_sheet = True
                else:
                    print (e)
    time_end = time.time()
    print_time("sheet to DWG", time_end, time_start)
    add_to_log(file_name + ".dwg", time_end - time_start)
    EA_UTILITY.show_toast(app_name = "Bilibili exporter",
                            title = "[{}.dwg] saved.".format(file_name),
                            image = "C:\Users\szhang\github\EnneadTab 2.0\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135.pulldown\icon.png",
                            message = "{} more to do in current document".format(total - counter))

    """

def print_PDF_from_sheet(sheet, print_manager, doc):
    #global print_manager
    print("-----")
    time_start = time.time()

    file_name = "{} - {}".format(sheet.SheetNumber, sheet.Name)
    if has_index:
        file_name = index_dict[sheet.SheetNumber] + "_" + file_name

    file_name = legalize_filename(file_name)
    print("preparing [{}].pdf".format(file_name))
    EA_UTILITY.remove_exisitng_file_in_folder(output_folder, file_name + ".pdf")


    #"""
    t = DB.Transaction(doc, "temp")
    t.Start()


    titleBlock = DB.FilteredElementCollector(doc, sheet.Id).OfCategory(DB.BuiltInCategory.OST_TitleBlocks).FirstElement()
    #print titleBlock.Symbol.Family.Name


    print_manager = doc.PrintManager
    print_manager.PrintToFile = True
    #print_manager.IsVirtual = True
    print_manager.SelectNewPrintDriver("Bluebeam PDF")
    # print_manager.Apply()



    print_manager.PrintSetup.CurrentPrintSetting = get_print_setting(doc,
                                                                    is_color = sheet.LookupParameter("Print_In_Color").AsInteger(),
                                                                    is_A1_paper = "A1" in titleBlock.Symbol.Family.Name)
    # print_manager.Apply()
    #t.Commit()
    #"""
    print("Print Setting Name = [{}]".format(print_manager.PrintSetup.CurrentPrintSetting.Name))
    print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
    print_manager.PrintRange = DB.PrintRange.Select
    view_set = DB.ViewSet()
    view_set.Insert(sheet)
    try:
        print_manager.ViewSheetSetting.InSession.Views = view_set
    except:
        print("InSession ViewSheetSet failed, trying with CurrentViewSheetSet...")
        print_manager.ViewSheetSetting.CurrentViewSheetSet.Views = view_set
    # print_manager.Apply()
    # t.Commit()
    #print print_manager.PrintToFileName
    reactivate_output()

    while True:
        try:
            try:
                print_manager.SubmitPrint(sheet)
            except:
                print("2nd method")
                print_manager.SubmitPrint()
            print("PDF export succesfully")
            break
        except Exception as e:
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                output.print_md("------**There is a file existing with same name, will attempt to save as {}**".format(new_name))

            elif "no views/sheets selected" in e:
                print (e)
                print("...")
                print(print_manager.PrintToFileName)
                print("problem sheet = {}".format(sheet.Name))
                has_non_print_sheet = True
            else:
                print (e)
                print(print_manager.PrintToFileName)
                print("problem sheet = {}".format(sheet.Name))
            break
    time_end = time.time()

    t.RollBack()
    #print t.GetStatus()
    cleanup_pdf_name()
    print_time("sheet to PDF", time_end, time_start)
    add_to_log(file_name + ".pdf", time_end - time_start)
    EA_UTILITY.show_toast(app_name = "Bilibili exporter",
                            title = "[{}.pdf] saved.".format(file_name),
                            image = "C:\Users\szhang\github\EnneadTab 2.0\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135.pulldown\icon.png",
                            message = "{} more to do in current document".format(total - counter))


def print_all_sheet_index():
    print("--------indexing all the sheets including file not printing now.--------")
    sorted_dict = sorted(index_dict.items(), key = lambda x: x[1])
    #print sorted_dict
    for key, value in sorted_dict:
        print("[{}] ---> {}".format(key, value))
    print("-------- end of index--------")


def index_all_sheets(docs, print_out = True):

    """
    consider using this format plot 'sequence_index_sheetname' so if people insert sheet in one plot it does not push all sheets after ward in other plot.
    """
    sheets = []
    for doc in docs:
        sheets.extend( get_sheets_from_doc(doc) )

    """
    sheets.sort(key = lambda x: x.LookupParameter("MC_$PlotID").AsString(), reverse = False)
    sheets.sort(key = lambda x: x.LookupParameter("Sheet_$Order").AsString(), reverse = False)
    sheets.sort(key = lambda x: x.SheetNumber, reverse = False)
    """

    sheets.sort(key = lambda x: (x.LookupParameter("MC_$PlotID").AsString() ,
                                x.LookupParameter("Sheet_$Order").AsInteger(),
                                x.SheetNumber), reverse = False)

    """
    for sheet in sheets:
        print("******")
        print(sheet.LookupParameter("MC_$PlotID").AsString(), sheet.LookupParameter("Sheet_$Order").AsInteger(), sheet.SheetNumber)
    """

    global index_dict
    for i, sheet in enumerate(sheets):
        index_dict[sheet.SheetNumber] = "{0:03}".format(i + 1)

    if print_out:
        print_all_sheet_index()

    #script.exit()
    return index_dict

def index_all_sheets_alt(docs, print_out = True):

    """
    consider using this format plot 'sequence_index_sheetname' so if people insert sheet in one plot it does not push all sheets after ward in other plot.
    """
    sheets = []
    for doc in docs:
        if doc is None:
            continue
        doc_sheets =  get_sheets_from_doc(doc)


        doc_sheets.sort(key = lambda x: (x.LookupParameter("Sheet_$Order").AsInteger(),
                                        x.SheetNumber), reverse = False)


        if "Site" in doc.Title:
            plot_sequence = 0
        elif "N3" in doc.Title:
            plot_sequence = 1
        elif "N4" in doc.Title:
            plot_sequence = 2
        elif "N5" in doc.Title:
            plot_sequence = 3
        elif "N6" in doc.Title:
            plot_sequence = 4
        else:
            plot_sequence = 999

        global index_dict
        for i, sheet in enumerate(doc_sheets):
            index_dict[sheet.SheetNumber] = "[{}]".format(plot_sequence) + "_{0:03}".format( i + 1)

        #sheets.extend( get_sheets_from_doc(doc) )
    if print_out:
        print_all_sheet_index()

    #script.exit()
    return index_dict




def is_sheet_in_current_issue_para(sheet):
    try:
        if "EA_INTERNAL PRINT" == key_para and sheet.LookupParameter(key_para).AsString() == u"\u25A0":
            return True
    except Exception as e:
        print("part A has issue.")
        print (e)
        print(sheet)
        print(sheet.SheetNumber)
        print(sheet.Name)
        note = "Part A:" + str(e) + "____" + sheet.SheetNumber + "___" + sheet.Name
        EA_UTILITY.dialogue(main_text = "send SZ screenshot", sub_text = note )
        script.exit()
    #print key_para
    #print sheet.Name
    #print sheet.LookupParameter(key_para).AsString()
    try:
        if sheet.LookupParameter("Sheet Note").AsString() == "Not Shared":
            return False
        if sheet.LookupParameter("Sheet Note").AsString() == "DD":
            return False
        if sheet.LookupParameter("Sheet Note").AsString() == "Internal":
            return False
        if sheet.LookupParameter("Sheet Note").AsString() == r"NOT ISSUE for 05/27":
            return False
        if sheet.LookupParameter("Sheet Note").AsString() == "not print":
            EA_UTILITY.show_toast(title = "sheet <{}>[{}] is set as 'not print' in sheet note.".format(sheet.SheetNumber, sheet.Name))
            return False

    except Exception as e:
        print("!!! Stop and see below:")
        print (e)
        print(sheet)
        print(sheet.SheetNumber)
        print(sheet.Name)
        note = "Part B:" + str(e) + "____" + sheet.SheetNumber + "___" + sheet.Name
        EA_UTILITY.dialogue(main_text = "send SZ screenshot", sub_text = note )
        script.exit()
        return False

    if not sheet.LookupParameter("Appears In Sheet List").AsInteger():
        return False


    try:
        if sheet.LookupParameter(key_para).AsString() == u"\u25A0":
            #print "qqqq"
            return True
        else:
            return False
    except Exception as e:
        print (e)
        return False


def get_sheets_from_doc(doc):
    if doc is None:
        return []
    if "2135_BiliBili" not in doc.Title:
        print("skip document: " + doc.Title)
        return []
    sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

    sheets = sorted(list(sheets), key = lambda x: x.SheetNumber)
    return filter(is_sheet_in_current_issue_para, sheets)


def pick_sheets(docs_to_process, is_using_all_sheets):
    """
    also filter to be in the picked_sheets
    sheets = filter(lambda x: x.Name in picked_sheets, sheets)

    picked_sheets = forms.SelectFromList.show(list, multiselect = True)

    if len is 0, then this have no effect

    """
    global picked_sheets
    all_docs = get_full_docs()

    picked_docs = filter(lambda x: x.Title in docs_to_process, all_docs)

    additional_picked_docs = filter(lambda x: x.Title in docs_to_process, get_all_open_docs())
    additional_picked_docs = [] ###if using old method, make addition pick doc as empty


    sheets = []
    for doc in picked_docs:
        sheets.extend( get_sheets_from_doc(doc) )

    for doc in additional_picked_docs:
        sheets.extend( get_sheets_from_doc(doc) )

    sheets = list(set(sheets))
    sheets.sort(key = lambda x:x.SheetNumber)


    if is_using_all_sheets:
        picked_sheets = sheets
        return

    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "[{}]-{}".format(self.SheetNumber, self.Name)


    option_list = [MyOption(x) for x in sheets]

    picked_sheets = forms.SelectFromList.show(option_list, multiselect = True, title = "only print those selected sheets")
    # no need to return value, becasue picked sheet si global....this is bad i know
    pass




def check_links_are_loaded():
    pass

def export_content_in_doc(doc):
    tG = DB.TransactionGroup(doc, "temp")
    tG.Start()

    time_start = time.time()
    output.print_md("##Currently printing from {}".format(doc.Title))
    sheets = get_sheets_from_doc(doc)


    def is_sheet_in_picked_sheets(sheet):
        # print "---"
        # print sheet.Name
        # print sheet.SheetNumber
        # print "-"
        find_match = False
        if sheet is None:
            return find_match
        for other_sheet in picked_sheets:
            # print other_sheet.Name
            # print other_sheet.SheetNumber
            if sheet.Name != other_sheet.Name:
                continue
            if sheet.SheetNumber != other_sheet.SheetNumber:
                continue
            find_match = True
            break

        # print find_match
        return find_match

    # print sheets
    # print picked_sheets
    sheets = filter(is_sheet_in_picked_sheets, sheets)
    # print sheets
    """
    need to compare both sheet number and sheet name to know it is a match.....linked doc sheets use different ID than actual viewsheet
    """

    global sheet_count
    sheet_count += len(sheets)
    #sheets.extend(get_sheets_from_doc(doc))

    """
    for sheet in sheets:
        print(sheet.Name)
    """


    #test sheets
    #sheets = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()
    #sheets = list(sheets)[10:15]
    print("*"*20)
    print("Below are sheets that will be printed.....")
    for sheet in sheets:
        print("\t{} - {}".format(sheet.SheetNumber, sheet.Name))
    print("*"*20)
    #script.exit()


    #get print setting
    if export_pdf:
        #global print_manager
        print_manager = doc.PrintManager
        print_manager.PrintToFile = True
        #print_manager.IsVirtual = True
        print_manager.SelectNewPrintDriver("Bluebeam PDF")
        print_manager.Apply()

    if export_dwg:
        global DWG_option
        DWG_export_setting = get_export_setting(doc, export_setting_name)
        DWG_option = DB.DWGExportOptions().GetPredefinedOptions(doc, DWG_export_setting.Name)

    global counter, total
    counter = 0
    total = len(sheets)
    if export_dwg and export_pdf:
        total *= 2



    try:
        pb_title = "Working on {}......".format(doc.Title)
        with forms.ProgressBar(title = "exporting sheet....{value} of {max_value}", step = 1, cancellable = True) as pb:
            for sheet in sheets:
                if pb.cancelled:
                    break
                if export_pdf:
                    #t = DB.Transaction(doc, "temp")
                    #t.Start()
                    counter += 1
                    print("\n\n#exporting {} of {}".format(counter, total))
                    print_PDF_from_sheet(sheet, print_manager, doc)
                    #t.Commit()
                    pb.update_progress(counter, total)

                if export_dwg:
                    counter += 1
                    print("\n\n#exporting {} of {}".format(counter, total))
                    export_DWG_from_sheet(sheet, doc)
                    pb.update_progress(counter, total)

                if export_image:
                    counter += 1
                    print("\n\n#exporting {} of {}".format(counter, total))
                    export_image_from_sheet(sheet, doc)
                    pb.update_progress(counter, total)


    except:
        for sheet in sheets:

            #debuger
            #if counter == 3:
                #break

            if export_pdf:
                counter += 1
                print("\n\n#exporting {} of {}".format(counter, total))
                print_PDF_from_sheet(sheet, print_manager, doc)

            if export_dwg:
                counter += 1
                print("\n\n#exporting {} of {}".format(counter, total))
                export_DWG_from_sheet(sheet, doc)

            if export_image:
                counter += 1
                print("\n\n#exporting {} of {}".format(counter, total))
                export_image_from_sheet(sheet, doc)



    time_end = time.time()
    print_time("print {} ".format(doc.Title), time_end, time_start, use_minutes = True)
    add_to_log(doc.Title, time_end - time_start)

    tG.RollBack()




    #script.exit()


def set_export_job_setting():

    global key_para
    #select the sheets by which issue black squere satus?

    filepath = r"I:\2135\0_BIM\10_BIM Management\Revision and Para List.txt"
    raw_data = EA_UTILITY.read_txt_as_list(filepath, use_encode = True)
    # revision_names = [x.split("-----")[0] for x in raw_data]
    para_names = [x.split("-----")[1] for x in raw_data]
    """
    para_names = [r"Issue 2021/12/31",\
                    r"Issue 2022/01/15",\
                    r"Issue 2022/02/25",\
                    r"Issue 2022/03/10"]
    """
    para_names.insert(0, "debug")#debug
    #para_names.append("EA_INTERNAL PRINT")
    para_names.insert(-1, "EA_INTERNAL PRINT")

    key_para = forms.ask_for_one_item(para_names, default = para_names[-1], prompt = "pick a issue", title = None)






    global has_index
    index_options = [["Plot_Index_SheetNum - SheetName", "(Recommended)"], "SheetNum - SheetName"]#"Index_SheetNum - SheetName",
    index_opt = EA_UTILITY.dialogue(main_text = "Do you want to add index prefix to PDF name so you when you combine they go by order?", options = index_options)
    """
    if index_opt == index_options[1]:
        has_index = True
        check_links_are_loaded()
        index_all_sheets(get_full_docs(), print_out = False)
    """
    if index_opt == index_options[0][0]:
        has_index = True
        check_links_are_loaded()
        index_all_sheets_alt(get_full_docs(), print_out = False)
    else:
        has_index = False
###index_all_sheets_alt



    global export_dwg
    global export_pdf
    global export_image
    global is_export_view_on_sheet
    file_types = ["pdf Only", "dwg Only", "pdf + dwg", "image Only(Always in Color)"] ### maybe add image as export option
    file_export_type, is_export_view_on_sheet = EA_UTILITY.dialogue(main_text = "What to export", options = file_types, verification_check_box_text = "Check me to include views on sheet as independent dwgs when exporting DWG.")
    if "pdf" in file_export_type:
        export_pdf = True
    if "dwg" in file_export_type:
        export_dwg = True
        global export_setting_name
        export_setting_name = get_export_setting(revit.doc, export_setting_name).Name
    if "image" in file_export_type:
        export_image = True

    global FORCE_BW_PDF
    FORCE_BW_PDF = False
    if export_pdf:
        bw_opts = ["Yes, Globally turn off color", ["No, keep color setting as defined on sheet parameter.", "Use this as default"]]
        res = EA_UTILITY.dialogue(main_text = "For the PDF, do you want to ignore local defined 'Print_In_Color' setting?", options = bw_opts)
        if res == bw_opts[0]:
            FORCE_BW_PDF = True


    if export_pdf:
        combine_opts = ["No, Thank you.", ["Yes, Combine all pdf to single PDF.", "(Handy!!))"]]
        res = EA_UTILITY.dialogue(main_text = "For the PDF, do you want to create combined PDF after export?", options = combine_opts)
        if res == combine_opts[1][0]:
            global IS_COMBINING_PDF
            IS_COMBINING_PDF = True
            global COMBINE_PDF_NAME
            from datetime import date
            COMBINE_PDF_NAME = forms.ask_for_string(default = "{}_XXX_Combined".format(date.today()), prompt = "Combined PDF name.")





    global output_folder
    #output_folder = op.expanduser("\Documents")
    #print output_folder
    output_folder = "{}\Documents".format(os.environ["USERPROFILE"])
    return
    """
    #print output_folder
    #get save folder
    output_folder = forms.pick_folder(title = "folder for the output PDF/DWG, best if you can create a empty folder")
    print(output_folder)
    script.exit()
    """


def proceed_all_sheets():
    orginal_doc_name = revit.doc.Title
    #primary_doc = revit.doc


    #get file name that want to process
    docs_to_process = forms.SelectFromList.show(bili_file_list,
                                            multiselect = True,
                                            title = "Select docs to process")

    if docs_to_process is None:
        script.exit()
    #open doc alrady open, doc that need to be opeend
    docs_already_open = [x.Title for x in get_top_revit_docs()]
    docs_to_be_opened_by_API = [x for x in docs_to_process if x not in docs_already_open]
    #print "docs alrady open = {}".format(docs_already_open)
    #print "docs to be opened = {}".format(docs_to_be_opened_by_API)
    #script.exit()
    exit_after_background_file_openning = False
    """
    if len(docs_to_be_opened_by_API) > 0:
        forms.alert("those files will need to be opened in the background before you move to next step, come back after it is done")
        exit_after_background_file_openning = True
    """

    #setting for all details
    if not exit_after_background_file_openning:
        set_export_job_setting()

    temp_res = EA_UTILITY.dialogue(main_text = "process all sheets from selected files?",  options = ["All Sheets in this issue", ["Let me select a few", "use manual select to export selected sheets."]])
    is_using_all_sheets = True if temp_res == "All Sheets in this issue" else False
    pick_sheets(docs_to_process, is_using_all_sheets)



    global COPY_FOLDER
    temp_res = EA_UTILITY.dialogue(main_text = "copy exported files to a folder after export?",  options = [["Yes, copy them","Handy if you are exporting things overnight"], "No need to copy files over"], sub_text = "If you used plot index naming format in previous step, it will create folder structure like this example.\n\nFolder you pick (example: record/2022-09-30 50% DD)\n    -N3\n        -PDFs\n            -A101_xx.pdf\n            -A102_xx.pdf\n        -DWGs\n            -A101_xx.dwg\n            -A102_xx.dwg\n\nDon't go too deep, for example above, the selection folder should say 'record/2022-09-30 50% DD', not 'N3'")
    COPY_FOLDER = forms.pick_folder(title = "this is where the final output will be copied into.") if "yes" in temp_res.lower() else None


    temp_res, will_abort = EA_UTILITY.dialogue(main_text = "sync and close doc after printing?", sub_text = "An additional Print-Log will autosave in your document folder regardless your choice below.", options = [["Sure", "All files will be closed after exporting"], ["No", "Files keep open after exporting"], "CANCEL THIS PRINT JOB NOW!"], verification_check_box_text = "..or click me to abort export. Last chance to cancel script in case you dont want to proceed anymore. When it is checked, all previous export setting is disgarded.")
    if temp_res is None or "CANCEL" in temp_res:
        return
    will_sync_and_close  = True if temp_res == "Sure" else False
    if will_abort:
        return

    #depress open hook
    EA_UTILITY.set_open_hook_depressed(is_depressed = True)
    EA_UTILITY.set_doc_change_hook_depressed(is_depressed = True)
    EA_UTILITY.print_note("my doc change hook depress satus = {}".format(EA_UTILITY.is_doc_change_hook_depressed()))

    time_start = time.time()
    #open background doc that neeed to be opeend
    for doc_name in docs_to_be_opened_by_API:
        open_doc_in_background(doc_name)
    #timer how long background files used to open
    time_end = time.time()
    global output
    output = script.get_output()
    if len(docs_to_be_opened_by_API) > 0:
        print_time("background loading {} files".format(docs_to_be_opened_by_API), time_end, time_start, use_minutes = False)

        ###!!!! no need to reactive primary doc if we are using post file name correction method
        #primary_doc = active_original_doc(orginal_doc_name).Document##function return UI doc ##try this to fix main doc pdf not print issue




    #open hook depression re-enable
    EA_UTILITY.set_open_hook_depressed(is_depressed = False)


    if exit_after_background_file_openning:
        script.exit()



    #print the index again
    if has_index:
        print_all_sheet_index()

    #get top level docs, which are the main doc in each file
    docs = get_top_revit_docs()


    #output.set_title("Export Assist")
    #output.center()
    #do work to them in loop
    time_start = time.time()

    for doc in docs:
        if doc.Title in docs_to_process:
            #if doc.Title == orginal_doc_name:
                #doc = primary_doc
            export_content_in_doc(doc)


        #####improvement#
        ##if doc title in "doc to be open by api", then close this doc after doc have been exported
        #####BUT, this will mess the for-loop if part of the list is being modified? need test???


    time_end = time.time()
    print("#"*20)
    print("all sheets from selected revit files have been printed.\nIssue parameter = [{}]".format(key_para))
    print_time("print {} sheets".format(sheet_count), time_end, time_start, use_minutes = True)


    for doc in docs:
        if doc.Title in docs_to_process:
            print("Date used on titleblock: [{}] = {}".format(doc.Title, get_issue_date_info(doc)))


    if export_image:
        primary_doc = active_original_doc(orginal_doc_name) #!!!when exporting image, the exportimage method will force activate the doc. So we need to switch back primary doc so other can be closed.


    #close daocs opeeedn by API
    close_docs_by_name(docs_to_be_opened_by_API)
    EA_UTILITY.set_doc_change_hook_depressed(is_depressed = False)
    EA_UTILITY.print_note("my doc change hook depress status = {}".format(EA_UTILITY.is_doc_change_hook_depressed()))


    output.set_title("Export Assist")
    #output.center()

    ###!!!!!!!!!!!!!!  only when debuging  !!!!!s
    #close_docs_by_name(orginal_doc_name) #!!!!!!!!!you can not close active doc, but you can open-active a plceholder doc or family doc and then close the orignal doc. to save
    is_skip_log = will_sync_and_close

    #consider making this a seperate tab
    output.next_page()
    print_ranked_log()

    if len(failed_export) != 0:
        print("\n\nThere are several view/sheet failed to export. See below and search your print log with 'Ctrl + F'")
        for item in failed_export:
            print(item)

    #print output_folder
    localtime = time.asctime( time.localtime(time.time()) ).replace(":","-")
    output.save_contents(output_folder + "\AutoSave Log_{}.html".format(localtime))



    if is_skip_log:
        output.save_contents(output_folder + "\AutoSave Log_Most Recent.html")
        time.sleep(30)
    else:
        if export_pdf:
            print("wait 15s so the reamining bluebeam PDF is outputed")
            time.sleep(20)
        """
        if "yes" == EA_UTILITY.dialogue(main_text = "end of printing. \nSave a print log?", options = ["yes", "no"]):
            output.save_contents(forms.save_file( file_ext = "html"))
        """

    cleanup_pdf_name()
    cleanup_jpg_name()
    delete_extra_file(output_folder,".PCP")
    delete_extra_file(output_folder,".PS")



    if has_non_print_sheet and not is_skip_log:
        EA_UTILITY.dialogue(main_text = "sheet from active doc not printed as PDF, check your documents folder")
    #send_email()

    #new function
    dump_exported_files_to_copy_folder()

    if will_sync_and_close:
        EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close()
        cleanup_pdf_name()
        cleanup_jpg_name()
    EA_UTILITY.print_note("my doc change hook depress satus = {}".format(EA_UTILITY.is_doc_change_hook_depressed()))
    EA_UTILITY.print_note("###END OF TOOL###")

    if IS_COMBINING_PDF:
        combine_final_pdf()

    EnneadTab.SOUNDS.play_sound("sound effect_mario stage clear.wav")
    total_time_second = int(time_end - time_start)
    total_time_min = int( (time_end - time_start)/ 60 )
    EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "Export done.",
                                    sub_text = "totla time = {} seconds = {} mins".format(total_time_second, total_time_min),
                                    window_title = "Bili Printer",
                                    button_name = "Close",
                                    self_destruct = 0,
                                    window_height = 300)







def print_ranked_log():

    main_log.sort(key = lambda x: x[0], reverse = True)
    output.print_md( "## Ranked export time below:")

    for item in main_log:
        time = item[0]
        if time > 120:
            mins = int((item[0])/60)
            output.print_md(":warning: < **{}** > use ***{}*** mins".format(item[1], mins))
        else:
            output.print_md("< **{}** > use ***{}*** seconds".format(item[1], time))


def get_all_open_docs():
    return EA_UTILITY.get_application().Documents

def get_full_docs():

    revit_links = DB.FilteredElementCollector(revit.doc).OfClass(DB.RevitLinkInstance).WhereElementIsNotElementType().ToElements()
    all_docs = [x.GetLinkDocument() for x in revit_links]#.insert(0, revit.doc)
    all_docs.insert(0, revit.doc)


    global WILL_IGNORE_LINKS

    good_docs = []
    for doc in all_docs:
        if not hasattr(doc, "Title"):
            if "Ignore Unloaded Links" in WILL_IGNORE_LINKS:
                continue


            WILL_IGNORE_LINKS = EA_UTILITY.dialogue(main_text = "There are revit link not loaded. This action will suggest to cancel.", sub_text = "Why links needed to be loaded?\n\nBackground link need to be loaded to correctly show views in the current file. They are also needed to properly indexing sheets across plot if you are printing other plot from current plot.\n\nBackground links such as:\n\t-Site File.\n\t-Bridge file.\n\t-Structure File.\n\t-N3 Special Geometry File", options = ["Exit", "Ignore Unloaded Links and continue"])
            if WILL_IGNORE_LINKS == "Exit":
                script.exit()
        else:
            good_docs.append(doc)


    return filter_loaded_docs(good_docs)

def filter_loaded_docs(docs):
    OUT = []
    for doc in docs:
        if doc is None:
            continue
        OUT.append(doc)
    return OUT


def combine_final_pdf():

    import os.path as op
    list_of_filepaths = []
    files = EA_UTILITY.get_filenames_in_folder(output_folder)
    files_exported_this_round = [x[1] for x in main_log]
    for file in files:
        if ".dwg" in file.lower():
            continue
        if ".jpg" in file.lower():
            continue
        if file in files_exported_this_round:
            file_path = op.join(output_folder, file)
            print("--combining PDF: {}".format(file_path))
            list_of_filepaths.append(file_path)

    combined_pdf_file_path = "{}\{}.pdf".format(output_folder, COMBINE_PDF_NAME)
    EA_UTILITY.merge_pdfs(combined_pdf_file_path, list_of_filepaths, reorder = True)
    if COPY_FOLDER:
        EA_UTILITY.copy_file_to_folder(combined_pdf_file_path, COPY_FOLDER)


def dump_exported_files_to_copy_folder():
    if COPY_FOLDER is None:
        return
    import os.path as op
    files = EA_UTILITY.get_filenames_in_folder(output_folder)
    files_exported_this_round = [x[1] for x in main_log]
    for file in files:
        if file in files_exported_this_round:
            file_path = op.join(output_folder, file)


            if "[1]" in file:
                plot_id = "N3"
            elif "[2]" in file:
                plot_id = "N4"
            elif "[3]" in file:
                plot_id = "N5"
            elif "[4]" in file:
                plot_id = "N6"
            elif "[0]" in file:
                plot_id = "Site"
            else :
                if "N3" in file:
                    plot_id = "N3"
                elif "N4" in file:
                    plot_id = "N4"
                elif "N5" in file:
                    plot_id = "N5"
                elif "N6" in file:
                    plot_id = "N6"
                else:
                    plot_id = "Site"


            if ".pdf" in file.lower():
                new_folder = "{}\{}\PDFs".format(COPY_FOLDER, plot_id)
                new_folder = EA_UTILITY.secure_folder(new_folder)

            elif ".dwg" in file.lower():
                new_folder = "{}\{}\DWGs".format(COPY_FOLDER, plot_id)
                new_folder = EA_UTILITY.secure_folder(new_folder)

            elif ".jpg" in file.lower():
                new_folder = "{}\{}\JPGs".format(COPY_FOLDER, plot_id)
                new_folder = EA_UTILITY.secure_folder(new_folder)

            else:
                new_folder = COPY_FOLDER[:]

            EA_UTILITY.copy_file_to_folder(file_path, new_folder)
################## main code below #####################
output = script.get_output()
output.close_others()
key_para = "temp"
sheet_count = 0
output_folder = "temp"
has_index = False
index_dict = {}
export_pdf = False
export_dwg = False
export_image = False
export_setting_name = "Empty"
DWG_option = ""
has_non_print_sheet = False
main_log = []
is_export_view_on_sheet = True
failed_export = []
WILL_IGNORE_LINKS = "default"
COPY_FOLDER = r"I:\2135\0_Progress Set\EA 2022-07-27 N3 progress print"
IS_COMBINING_PDF = False
#print_manager = ""
app = revit.doc.Application
from pyrevit import _HostApplication as host_app
#host_app = pyrevit._HostApplication

"""
qqq = (90, "qq")
print(qqq)
print(qqq[0])
script.exit()
"""


#cloud_path = "BIM 360://2135_Bilibili Shanghai Headquarters/2135_BiliBili SH HQ_N4.rvt"
cloud_path = r"BIM 360://2135_Bilibili Shanghai Headquarters/***.rvt"

GUID_list = [
            ["2135_BiliBili SH HQ_N3", "7bb487db-c370-408e-9a97-9441ef91c51c", "9652bd4b-03b2-4016-8af3-2742efa27968"],
            ["2135_BiliBili SH HQ_N4", "7bb487db-c370-408e-9a97-9441ef91c51c", "ca4336c2-ea68-4d16-97a5-32c09a7c607b"],
            ["2135_BiliBili SH HQ_N5", "7bb487db-c370-408e-9a97-9441ef91c51c", "bc6dc5d7-8833-4564-aa74-c64dc14f50a1"],
            ["2135_BiliBili SH HQ_N6", "7bb487db-c370-408e-9a97-9441ef91c51c", "50ce9b1b-6ecf-4a7b-aec1-8f0af5acfe06"],
            ["2135_BiliBili SH HQ_Site", "7bb487db-c370-408e-9a97-9441ef91c51c", "8e18fa0b-26ec-4ddd-99d1-799953f5e2b3"]
            ]


bili_file_list = ["2135_BiliBili SH HQ_N3",
                "2135_BiliBili SH HQ_N4",
                "2135_BiliBili SH HQ_N5",
                "2135_BiliBili SH HQ_N6",
                "2135_BiliBili SH HQ_Site"]



action_options = [ ["Exporting sheets from model(s)", "by clicking this it is assumed you have recently reload ALL link to lastest info, unloaded rvt links can make indexing skips plot."],
                    ["[Folder Cleanup] Delete .PS and .PCP files", "clear all files with these extension in selected folder"],
                    ["[Folder Cleanup] Delete .PS, .PCP, .pdf, .dwg, .png and .jpg files", "clear all files with these extension in selected folder"],
                    "Tell me how to prevent bluebeam file name dialogue from showing up on every file",
                    "fix pdf name from RAM limit(beta)",
                    "cancel action"]
action = EA_UTILITY.dialogue(main_text = "pick a action:", options = action_options, sub_text = "in version 3.3, script will open background file for document that is not open, you will not see the background revit file. This is to enssure nesting link loaded to upper level when exporting.\n\nIf PDF fail to come out, that might be bluebeam jam up the print queue. Open windows task manager. This can force the bluebeam glitch to clean out and all your backlog PDF will be released.")



if action == action_options[0][0]:

    sync_current_session_opts = [["Sync all open documents now and try printing later...","(Especially before you are printing a lot of sheets)"], "Ignore syncing now and Continue..."]
    if EA_UTILITY.dialogue(main_text = "Friendly reminder:\nBefore print do you want to sync all open document, just in case you crash?", options = sync_current_session_opts) == sync_current_session_opts[0][0]:
        EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close(close_others = False)


    proceed_all_sheets()
    #consider auto deelte PCP file after script run
    #consider eliminate the process to pick folder, just use user document folder by default
    #consider using option to print color or BW


elif action == action_options[1][0]:
    fix_folder = forms.pick_folder(title = "folder to fix extra dot")
    remove_extra_dot()
    pcp_count = delete_extra_file(fix_folder,".PCP") #if self.clearPCP else 0
    ps_count = delete_extra_file(fix_folder,".PS") #if self.clearPS else 0
    script.exit()
elif action == action_options[2][0]:
    fix_folder = forms.pick_folder(title = "folder to fix extra dot")
    remove_extra_dot()
    delete_extra_file(fix_folder,".PCP")
    delete_extra_file(fix_folder,".PS")
    delete_extra_file(fix_folder,".PDF")
    delete_extra_file(fix_folder,".DWG")
    delete_extra_file(fix_folder,".JPG")
    delete_extra_file(fix_folder,".PNG")
    script.exit()
elif action == action_options[3]:
    show_setting_helper()
    script.exit()
elif action == action_options[4]:
    EA_UTILITY.dialogue(main_text = "beta concept: if PDF print fail to give index name as desired, use me to replace file name by looking up index table.")
    script.exit()
else:
    script.exit()
