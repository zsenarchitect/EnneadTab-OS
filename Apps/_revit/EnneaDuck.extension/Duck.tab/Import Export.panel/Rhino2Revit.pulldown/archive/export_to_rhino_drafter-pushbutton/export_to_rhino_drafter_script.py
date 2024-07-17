#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Get the content of current view to Rhino as background, so you can\
 draft more effeciently with advanced Rhino techniques such as CurveBoolean.\n\n\
A empty Rhino will be fired up for you.\n\nIt worth mentioning that any non-perspective \
Revit view can be exported and bring back as background:)"
__title__ = "Export to Rhino Drafter"
__youtube__ = "https://youtu.be/UGRFjFWCVqU"
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import EnneadTab
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore

import time


def get_export_setting(doc, setting_name = "Empty"):
    existing_dwg_settings = DB.FilteredElementCollector(doc).OfClass(DB.ExportDWGSettings).WhereElementIsNotElementType().ToElements()


    def pick_from_setting():
        sel_setting = None
        attempt = 0
        while sel_setting == None:
            if attempt > 2:
                break
            sel_setting = forms.SelectFromList.show(existing_dwg_settings, \
                                                    name_attr = "Name", \
                                                    button_name='prefer setting with internal coordination system', \
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



def export_dwg_action(file_name, view_or_sheet, doc, output_folder, DWG_option, additional_msg = ""):
    time_start = time.time()
    if r"/" in file_name:
        file_name = file_name.replace("/", "-")
        print("Windows file name cannot contain '/' in its name, i will replace it with '-'")
    print("preparing [{}].dwg".format(file_name))
    EA_UTILITY.remove_exisitng_file_in_folder(output_folder, file_name + ".dwg")
    view_as_collection = EA_UTILITY.list_to_system_list([view_or_sheet.Id])
    max_attempt = 10
    attempt = 0
    #print view_as_collection
    #print view_or_sheet
    while True:
        if attempt > max_attempt:
            print("Give up on <{}>, too many failed attempts, see reason above.".format(file_name))
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
    additional_msg = "exporting DWG takes {}s".format( time_end - time_start)
    print(additional_msg)

    EA_UTILITY.show_toast(app_name = "Draft Transfer Exporter",
                            title = "[{}.dwg] saved.".format(file_name),
                            message = additional_msg)



def export_to_rhino_drafter(doc):
    # stop if doing sheet sheet
    if str(doc.ActiveView.ViewType) not in ["Detail", "Section", "AreaPlan", "Elevation", "FloorPlan", "CeilingPlan", "DraftingView"]:
        print("Cannot do it in view type " + str(doc.ActiveView.ViewType))
        print("Ask SZ for suggestion, tool canceled.")
        return
    #if doc.ActiveView.ViewType not in



    # save time by srat rhin oearly
    open_template_rhino(doc)


    crop_region_shape_manager = doc.ActiveView.GetCropRegionShapeManager ()
    if crop_region_shape_manager.Split :
        EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "The view appears to have view break.", sub_text = "You can still draft in Rhino, but be aware that Rhino will not understand Revit view break in dwg, so when importing back, the draft might see partial shift.", self_destruct = 10)




    # export current view
    DWG_export_setting = get_export_setting(doc, setting_name = "Empty")
    DWG_option = DB.DWGExportOptions().GetPredefinedOptions(doc, DWG_export_setting.Name)

    file_name = "EA_TRANSFER_DRAFT_BACKGROUND"
    view = doc.ActiveView
    output_folder = EA_UTILITY.get_EA_local_dump_folder()
    export_dwg_action(file_name, view, doc, output_folder, DWG_option)




    EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "An empty Rhino is opening. You can use it to draft polylines and arcs now. Or use surface to draft filled region.", sub_text = "\n\nRemember, Revit primarily only take line and true arc, so not all your freeform Nurbs in Rhino can be regenerated in Revit.", self_destruct = 10)

    # export a dump txt to inlcude all OST line style


def open_template_rhino(doc):
    try:
        revit_unit = doc.GetUnits().GetFormatOptions (DB.UnitType.UT_Length ).DisplayUnits
        revit_unit =  str(revit_unit).replace("DUT_", "").lower()
        print(revit_unit)
    except:

        revit_unit = doc.GetUnits().GetFormatOptions (EA_UTILITY.lookup_unit_spec_id("length") ).GetUnitTypeId().TypeId
        revit_unit = str(revit_unit).split("-")[0].split("unit:")[1]
        print(revit_unit)
    """
    possible revit unit
    feet_fractional_inches
    feetFractionalInches
    feet
    inches
    millimeters
    """

    """
    possible rhin ounit
    feet, feet & inches
    inches, feet & inches
    feet
    inches
    millimeters
    """
    if "feet_fractional_inches" == revit_unit or "feetFractionalInches" == revit_unit:
        revit_unit = "feet, feet & inches"





    # open template
    import os
    rhino_template_folder = r"{}\AppData\Roaming\McNeel\Rhinoceros\7.0\Localization\en-US\Template Files".format(os.environ["USERPROFILE"])
    for template in EA_UTILITY.get_filenames_in_folder(rhino_template_folder):
        #print template
        if revit_unit in template.lower():
            break


    file_path = rhino_template_folder + "\\" + template
    EA_UTILITY.copy_file_to_folder(file_path, EA_UTILITY.get_EA_local_dump_folder())
    file_path = EA_UTILITY.get_EA_local_dump_folder() + "\\" + template
    EA_UTILITY.open_file_in_default_application(file_path)


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    export_to_rhino_drafter(doc = __revit__.ActiveUIDocument.Document # pyright: ignore)
