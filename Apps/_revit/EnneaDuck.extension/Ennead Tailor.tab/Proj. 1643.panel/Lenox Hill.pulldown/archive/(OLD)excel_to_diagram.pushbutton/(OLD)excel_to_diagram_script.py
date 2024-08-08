#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "(OLD)Excel2Diagram"

# from pyrevit import forms #
from calendar import c
from random import sample
import re
from weakref import ref
from pyrevit import script #


from EnneadTab import ERROR_HANDLE, EXCEL, FOLDER, NOTIFICATION, TIME
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_VIEW, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


EXCEL_FILE = "J:\\1643\\2_Master File\\B-70_Programming\\01_Program & Analysis\\EA 2024-03-21 EA Program.xlsx"
FAMILY_NAME = "AreaShader"
WORKING_VIEW = "SK-G09_10_Program Shading"


# just the key is important now... the value is ingored
CONTAINER_FACTOR_MAP = {
    "10.0":3,
    "10.1":1.8,
    "10.2":1.8,
    "11.0":2,
    "11.1":1.8,
    "11.6":1.8,
    "13.0":1.8,
    "14.0":1.8,
    "15.0":2,
    "15.1":1.5,
    "15.3":1.5,
    "15.4":1.5,
    "16.0":1.4,
    "16.1":1.2
    }


USED_NAMES_IN_EXCEL = set()


@ERROR_HANDLE.try_catch_error()
def excel_to_diagram():
    REVIT_VIEW.set_active_view_by_name(WORKING_VIEW)
    solid_id = REVIT_SELECTION.get_solid_fill_pattern_id(doc)


    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    temp = FOLDER.copy_file_to_local_dump_folder(EXCEL_FILE, "temp.xls")
    data = EXCEL.read_data_from_excel(temp, worksheet="LHH_Public Program")

    data = data[5:] # remove header roows
    color = -1,-1,-1

    for line in data:

        
        line = line[6:] # remove bad columns from left
        
        if line[0] == line[1] == line[2] == "":
            #empty line
            continue

        
        print ("\n\n")
        print (line)

        if line[0] != "":
            ref_num = line[0]
            title = line[1]
        else:
            ref_num = line[1]
            title = line[2]

        # ignote this line, just make sense in excel, not related to diagram

        if "NEED AMBULANCE/EMERGENCY DEPARTMENT CATEGORY" in str(ref_num):
            continue
            
        #round to 2 digit
        if isinstance(ref_num, float):
            ref_num = round(float(ref_num), 3)
            ref_num = str(ref_num)


        count = line[3] if line[3] != "" else 1
        unit_area = line[4] if line[4] != "" else -1

  
        for index in [6, 8, 11]:
            program_area_DGSF = line[index]
            try:
                program_area_DGSF = float(program_area_DGSF)
                if program_area_DGSF == 0:
                    continue
                if index == 11:
                    is_remote = True
                else:
                    is_remote = False
                break
            except:
                pass
        try:
            program_area_NSF = float(line[index-1])
        except:
            program_area_NSF = 0

            

        note = str(line[7])

        if line[16] != "":
            try:
                color = line[16].split("-")
                color = [int(x) for x in color]
            except:
                print (color)

        
        if title == "Mother/Baby Dedicated Discharge":
            ref_num = "11.10"

        print ("ref num = " + ref_num)
        print ("title = " + title)
        print ("count = " + str(count))
        print ("unit area = " + str(unit_area))
        print ("DGSF program area = " + str(program_area_DGSF))
        print ("NSF program area = " + str(program_area_NSF))
        print ("note = " + note)
        print ("color = " + str(color))

        
        graphic_override = DB.OverrideGraphicSettings ()
        graphic_override.SetSurfaceForegroundPatternColor (DB.Color(*color))
        graphic_override.SetSurfaceForegroundPatternId  (solid_id)

        
        if "TOTAL PUBLIC" in ref_num:
            # all the SUMMERY
            process_line(ref_num, title, count, unit_area, program_area_DGSF, note, graphic_override, is_remote)
        else:
            if ref_num not in CONTAINER_FACTOR_MAP:
                # all the smallest bubble
                process_line(ref_num, title, count, unit_area, program_area_NSF or program_area_DGSF, note, graphic_override, is_remote)
            else:
                if ref_num in ["13.0", "16.0"]:
                    process_line(ref_num, title, count, unit_area, program_area_DGSF, note, graphic_override, is_remote)
                elif ref_num.endswith("0"):
                    # all the other top level container 
                    process_line(ref_num, title + "(NSF)", count, unit_area, program_area_NSF, note, graphic_override, is_remote)# this is for the summery view
                    process_line(ref_num, title, count, unit_area, program_area_DGSF, note, graphic_override, is_remote)
                else:
                    # all the middle level container, it need to show twice

                    # show as inside top level containner
                    process_line(ref_num, title, count, unit_area, program_area_NSF or program_area_DGSF, note, graphic_override, is_remote)


                    # show as in containing all the smaller
                    title += "_SmallContainer"
                    process_line(ref_num, title, count, unit_area, program_area_DGSF, note, graphic_override, is_remote)

  

    t.Commit()
    NOTIFICATION.messenger("Bubble diagram data updated from Excel")

    types_in_proj = [doc.GetElement(x) for x in REVIT_FAMILY.get_family_by_name(FAMILY_NAME).GetFamilySymbolIds()]
    type_names_in_proj = [x.LookupParameter("Type Name").AsString() for x in types_in_proj]

    names_in_proj_but_not_in_excel = set(type_names_in_proj) - USED_NAMES_IN_EXCEL
    for name in names_in_proj_but_not_in_excel:
        NOTIFICATION.messenger("Name in project but not in Excel: " + name)
        samples = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(FAMILY_NAME, name)
        if len(samples) != 0:
            sample = samples[0]
            print("Name in project but not in Excel: " + output.linkify(sample.Id, title = name))
        else:
            print("Name in project but 0 instances, should purge: " + name)

    names_in_excel_but_not_in_proj = USED_NAMES_IN_EXCEL - set(type_names_in_proj)
    for name in names_in_excel_but_not_in_proj:
        print("Name in Excel but not in project: " + name)


def process_line(ref_num, title, count, unit_area, program_area, note, graphic_override, is_remote):
    is_ok = False

    try:
        program_area = float(program_area)
        if program_area != 0:
            is_ok = True
            note = ""
    except:
        pass

    if not is_ok:
        NOTIFICATION.messenger("Invalid program area for " + ref_num + " " + title)
        program_area = 499
        if  "CANCEL:" not in note:
            note = "!!!!!!!!INVALID AREA: " + note


    # try find instance with ref_num, if not exist, create one
    type_name = "{}_{}".format(ref_num, title)
    global USED_NAMES_IN_EXCEL
    USED_NAMES_IN_EXCEL.add(type_name)

    family_type = REVIT_FAMILY.get_family_type_by_name(FAMILY_NAME, type_name, create_if_not_exist=True)

    instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(FAMILY_NAME, type_name)
    if len(instances) == 0:
        instance = doc.Create.NewFamilyInstance(DB.XYZ(0, 0, 0), family_type, doc.ActiveView)
        if program_area > 0:
            instance.LookupParameter("W").Set(program_area**0.5)
        instances = [instance]
    # elif len(instances) == 1:
    #     pass
    # elif len(instances) > 1:
    #     NOTIFICATION.messenger("More than one instance of type {} found.".format(type_name))



    if "CANCEL:" in note:
        family_type.LookupParameter("is_cancel").Set(1)
    else:
        family_type.LookupParameter("is_cancel").Set(0)

    

    # print (family_type)
    # update the data to instance
    family_type.LookupParameter("Count").Set(count)
    family_type.LookupParameter("UnitArea").Set(unit_area)


        
    family_type.LookupParameter("ProgramArea").Set(program_area)
    family_type.LookupParameter("ProgramNote").Set(note)
    family_type.LookupParameter("ProgramRefNum").Set(ref_num)

    if "_SmallContainer" in title:
        title = title.replace("_SmallContainer", "")
    family_type.LookupParameter("ProgramTitle").Set(title)

    if is_remote:
        family_type.LookupParameter("is_remote").Set(1)
        family_type.LookupParameter("ProgramRemoteNote").Set("(REMOTE)")
    else:
        family_type.LookupParameter("is_remote").Set(0)
        family_type.LookupParameter("ProgramRemoteNote").Set("")


    # do not scale up becasue now using seperate container and it is eaiser to find a balanced number manuall and keep using that
    # container_factor = CONTAINER_FACTOR_MAP.get(ref_num, 1)
    # family_type.LookupParameter("container_factor").Set(container_factor)

    for instance in instances:
        host_view = doc.GetElement(instance.OwnerViewId)
        host_view.SetElementOverrides (instance.Id, graphic_override)
        instance.LookupParameter("Comments").Set("Updated {}".format(TIME.get_formatted_current_time()))





################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    excel_to_diagram()
    







