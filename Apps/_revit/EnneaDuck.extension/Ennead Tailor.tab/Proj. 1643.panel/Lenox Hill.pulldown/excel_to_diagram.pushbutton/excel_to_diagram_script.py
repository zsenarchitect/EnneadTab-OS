#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Excel2Diagram"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE, EXCEL, FOLDER, NOTIFICATION, TIME
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY, REVIT_VIEW, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


EXCEL_FILE = "J:\\1643\\2_Master File\\B-70_Programming\\01_Program & Analysis\\EA 2024-05-03 EA Program.xlsx"
SHADER_FAMILY_NAME = "AreaShader"
TITLER_FAMILY_NAME = "TitleMaker"
WORKING_VIEW = "SK-G09_10_Program Shading"


EXCLUSIVE_TITLE_MAKERS = [
    "10.1",
    "10.2",
    "15.1",
    "15.3",
    "15.4",
    "16.1"
]



USED_NAMES_IN_EXCEL = set()

class LineData:


    def __init__(self, line):
        self.line = line

    def get_column(self, column_name):
        return self.line[EXCEL.get_column_index(column_name)]

    def get_next_column(self, column_name):
        return self.line[EXCEL.get_column_index(column_name) + 1]

    for i in range(ord('A'), ord('Z') + 1):
        column_name = chr(i)
        locals()[column_name] = property(lambda self, column_name=column_name: self.get_column(column_name))
        

    
@ERROR_HANDLE.try_catch_error
def excel_to_diagram(doc):
    REVIT_VIEW.set_active_view_by_name(WORKING_VIEW)
    solid_id = REVIT_SELECTION.get_solid_fill_pattern_id(doc)


    
    t = DB.Transaction(doc, __title__)
    t.Start()
    
    temp = FOLDER.copy_file_to_local_dump_folder(EXCEL_FILE, "temp.xls")
    data = EXCEL.read_data_from_excel(temp, worksheet="LHH_Public Program")

    data = data[5:] # remove header roows
    color = -1,-1,-1

    for line in data:

        

        if line[6:][0] == line[6:][1] == line[6:][2] == "":
            #empty line
            continue

        
        print ("\n\n")
        print (line[6:])
        line_data = LineData(line)

        if line_data.G != "":
            ref_num = line_data.G
            title = line_data.get_next_column("G")
        else:
            ref_num = line_data.H
            title = line_data.get_next_column("H")


        if isinstance(ref_num, str) and ref_num.startswith("TOTAL"):
            continue


        #round to 2 digit
        if isinstance(ref_num, float):
            ref_num = round(float(ref_num), 3)
            ref_num = str(ref_num)
        
        if title == "Mother/Child Dedicated Discharge":
            ref_num = "11.10"


        count = int(line_data.J) if line_data.J != "" else 1
        unit_area = int(line_data.K) if line_data.K != "" else -1


        if line_data.L == "TBD":
            continue




        for index in ["L",  "S"]:
            program_area_NSF = line_data.get_column(index)

            try:
                program_area_NSF = float(program_area_NSF)
                if program_area_NSF != 0:
                    break
            except:
                pass

        for index in ["M", "O", "T"]:
            program_area_DGSF = line_data.get_column(index)

            try:
                program_area_DGSF = float(program_area_DGSF)
                if index == "T":
                    is_remote = True
                else:
                    is_remote = False
                if program_area_DGSF != 0:
                    break
            except:
                pass

        if isinstance(program_area_NSF, str):
            program_area_NSF = 0
        if isinstance(program_area_DGSF, str):
            program_area_DGSF = 0


        if ref_num in ["14.2", "14.3", "10.2C", "10.2D"]:
            is_remote = True
            program_area_NSF = 300




            

        note = str(line_data.N)

        if line_data.W != "":
            try:
                color = line_data.W.split("-")
                color = [int(x) for x in color]
            except:
                print (color)


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

        
        


        if ref_num in EXCLUSIVE_TITLE_MAKERS:
            update_titler(ref_num, title, program_area_NSF, program_area_DGSF)
        else:
            process_line(ref_num, title, count, unit_area, program_area_NSF, program_area_DGSF, note, graphic_override, is_remote)
            if ref_num == "11.10":# give mather baby a special treamnt
                update_titler(ref_num, title, program_area_NSF, program_area_DGSF)
            elif ref_num[-1].isalpha() or str(ref_num).endswith("0"):
                # if has leeter in name, that is a sub item, do not need to make title
                # if ref_num ends with 0, that is a department item, do not need to make title
                pass
            else:
                update_titler(ref_num, title, program_area_NSF, program_area_DGSF)
  

    t.Commit()
    
    NOTIFICATION.messenger("Bubble diagram data updated from Excel")

    types_in_proj = [doc.GetElement(x) for x in REVIT_FAMILY.get_family_by_name(SHADER_FAMILY_NAME).GetFamilySymbolIds()]
    type_names_in_proj = [x.LookupParameter("Type Name").AsString() for x in types_in_proj]

    names_in_proj_but_not_in_excel = set(type_names_in_proj) - USED_NAMES_IN_EXCEL
    for name in names_in_proj_but_not_in_excel:
        NOTIFICATION.messenger("Name in project but not in Excel: " + name)
        samples = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(SHADER_FAMILY_NAME, name)
        if len(samples) != 0:
            sample = samples[0]
            print("Name in project but not in Excel: " + output.linkify(sample.Id, title = name))
        else:
            print("Name in project but 0 instances, should purge: " + name)

    names_in_excel_but_not_in_proj = USED_NAMES_IN_EXCEL - set(type_names_in_proj)
    for name in names_in_excel_but_not_in_proj:
        print("Name in Excel but not in project: " + name)

@ERROR_HANDLE.try_pass
def process_line(ref_num, title, count, unit_area, program_area_NSF, program_area_DGSF, note, graphic_override, is_remote):


    if program_area_DGSF != 0 or program_area_NSF != 0:
        is_ok = True
        note = ""
    else:
        is_ok = False


    if not is_ok and not is_remote:
        NOTIFICATION.messenger("Invalid program area for " + ref_num + " " + title)
        if program_area_DGSF == 0:
            program_area_DGSF = 499 
            note = "!!!!INVALID DGSF AREA: " + note

        if program_area_NSF == 0:
            program_area_NSF = 499
            note = "!!!!INVALID NSF AREA: " + note


    if ref_num in ["11.10",
                    "11.11",
                    "11.12",
                    "15.1H"]:
        program_area_NSF = 19 # this is to ensure those special program geo shaper does not fail...They are never assigned with real data in program

    # try find instance with ref_num, if not exist, create one
    type_name = "{}_{}".format(ref_num, title)
    global USED_NAMES_IN_EXCEL
    USED_NAMES_IN_EXCEL.add(type_name)

    family_type = REVIT_FAMILY.get_family_type_by_name(SHADER_FAMILY_NAME, type_name, create_if_not_exist=True)

    instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(SHADER_FAMILY_NAME, type_name)
    if len(instances) == 0:
        instance = doc.Create.NewFamilyInstance(DB.XYZ(0, 0, 0), family_type, doc.ActiveView)
        family_type.LookupParameter("container_factor").Set(1)
        if program_area_DGSF > 0:
            instance.LookupParameter("W").Set(program_area_DGSF**0.5)
        instances = [instance]


    if "CANCEL:" in note:
        family_type.LookupParameter("is_cancel").Set(1)
    else:
        family_type.LookupParameter("is_cancel").Set(0)

    

    # print (family_type)
    # update the data to instance
    family_type.LookupParameter("Count").Set(count)
    family_type.LookupParameter("UnitArea").Set(unit_area)

    if count != 1:
        #family_type.LookupParameter("divider").Set(count)# add solid line to eq divide the bubble
        area_special_note = "{}@{} {}".format(count, unit_area, note)
        family_type.LookupParameter("AreaSpecialNote").Set(area_special_note)
        family_type.LookupParameter("show_special_note").Set(1)
        note = None
    else:
        family_type.LookupParameter("show_special_note").Set(0)
        family_type.LookupParameter("AreaSpecialNote").Set(" ")
        note = None




        
    family_type.LookupParameter("ProgramAreaDGSF").Set(program_area_DGSF)
    family_type.LookupParameter("ProgramAreaNSF").Set(program_area_NSF)
    if note:
        family_type.LookupParameter("show_note").Set(1)
        family_type.LookupParameter("ProgramNote").Set(note)
    else:
        family_type.LookupParameter("show_note").Set(0)


    family_type.LookupParameter("ProgramRefNum").Set(ref_num)


    if is_remote:
        family_type.LookupParameter("is_remote").Set(1)
        family_type.LookupParameter("ProgramRemoteNote").Set("(REMOTE)")
        title += "(REMOTE)"
    else:
        family_type.LookupParameter("is_remote").Set(0)
        family_type.LookupParameter("ProgramRemoteNote").Set("")


    family_type.LookupParameter("ProgramTitle").Set(title)

    

    for instance in instances:
        host_view = doc.GetElement(instance.OwnerViewId)
        host_view.SetElementOverrides (instance.Id, graphic_override)
        instance.LookupParameter("Comments").Set("Updated {}".format(TIME.get_formatted_current_time()))




@ERROR_HANDLE.try_pass
def update_titler(ref_num, title, program_area_NSF, program_area_DGSF):






    # try find instance with ref_num, if not exist, create one
    type_name = "Title_{}_{}".format(ref_num, title)


    family_type = REVIT_FAMILY.get_family_type_by_name(TITLER_FAMILY_NAME, type_name, create_if_not_exist=True)

    instances = REVIT_FAMILY.get_family_instances_by_family_name_and_type_name(TITLER_FAMILY_NAME, type_name)
    if len(instances) == 0:
        instance = doc.Create.NewFamilyInstance(DB.XYZ(0, 0, 0), family_type, doc.ActiveView)
        instances = [instance]

        
    family_type.LookupParameter("ProgramAreaDGSF").Set(program_area_DGSF)
    family_type.LookupParameter("ProgramAreaNSF").Set(program_area_NSF)
    family_type.LookupParameter("ProgramRefNum").Set(ref_num)

    family_type.LookupParameter("ProgramTitle").Set(title)




    

    for instance in instances:
        instance.LookupParameter("Comments").Set("Updated {}".format(TIME.get_formatted_current_time()))




################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    excel_to_diagram(doc)
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







