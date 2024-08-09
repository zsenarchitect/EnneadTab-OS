#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Depreciated"
__title__ = "49_Export No Sheet View as Jpgs(Depreciated)"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import time
import os
import os.path as op
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore


def created_by_who(view):
    view_history = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, view.Id)
    return view_history.Creator


def export_image_from_view(view, doc, adding_creator):

    print("-----")
    global counter
    counter += 1

    time_start = time.time()

    file_name = view.Name
    if adding_creator:
        file_name = "Created By [{}]_{}".format(created_by_who(view), view.Name)

    """
    file_name = file_name.replace("{", "[")
    file_name = file_name.replace("}", "]")
    """

    print("preparing [{}].jpg".format(file_name))
    

    #output_folder = "{}\Documents".format(os.environ["USERPROFILE"])
    output_folder = "{}\Documents\{}".format(os.environ["USERPROFILE"], "###UnSheeted Views Jpgs for [{}]".format(doc.Title))

    #dir = os.path.join("C:\\","temp","python")
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)


    opts = DB.ImageExportOptions()
    opts.FilePath = output_folder + r'\{}.jpg'.format(file_name)
    opts.ImageResolution = DB.ImageResolution.DPI_300
    opts.ExportRange = DB.ExportRange.SetOfViews
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 6000
    opts.SetViewsAndSheets(EA_UTILITY.list_to_system_list([view.Id]))

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
    EA_UTILITY.show_toast(app_name = "Bilibili exporter",
                            title = "[{}.jpg] saved.".format(file_name),
                            image = "C:\Users\szhang\github\EnneadTab 2.0\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135.pulldown\icon.png",
                            message = "{} more to do in current document".format(total - counter))



def cleanup_jpg_name(output_folder, desired_name, keyword):
    EA_UTILITY.remove_exisitng_file_in_folder(output_folder, desired_name + ".jpg")

    #print keyword

    file_names = os.listdir(output_folder)

    for file_name in file_names:
        if desired_name in file_name and ".jpg" in file_name.lower():
            #new_name = file_name.split(keyword)[0]
            new_name = desired_name

            try:
                os.rename(op.join(output_folder, file_name),op.join(output_folder, new_name + ".jpg"))
            except Exception as e:
                print("skip {} becasue: {}".format(file_name, e))

def is_no_sheet(view):

    if str(view.ViewType) in [ "Legend", "Schedule", "SystemBrowser", "ProjectBrowser", "DrawingSheet"]:
        return False
    if "revision" in view.Name.lower():
        return False
    if "schedule" in view.Name.lower():
        return False
    if view.IsTemplate:
        return False
    if view.LookupParameter("Sheet Number") is None:
        return True
    if view.LookupParameter("Sheet Number").AsString() == "---":
        return True
    return False

################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:


opts = ["Yes", "No"]
res = EA_UTILITY.dialogue(main_text = "Should it prefix the creator name?", options = opts)
if not res:
    script.exit()
if res == opts[0]:
    adding_creator = True
else:
    adding_creator = False

all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()

no_sheet_views = filter(is_no_sheet, all_views)
no_sheet_views.sort(key = lambda x:x.Name)
no_sheet_views = forms.SelectFromList.show(no_sheet_views, multiselect = True, name_attr = "Name", title = "Search the view names that you want to export.")
if no_sheet_views is None:
    script.exit()
total = len(no_sheet_views)
counter = 0

t = DB.Transaction(doc, "export no sheet views")
t.Start()
will_sync_and_close = EA_UTILITY.do_you_want_to_sync_and_close_after_done()
map(lambda x: export_image_from_view(x, doc, adding_creator), no_sheet_views)
t.Commit()
if will_sync_and_close:
    EnneadTab.REVIT.REVIT_APPLICATION.sync_and_close()


print("################### finish")
