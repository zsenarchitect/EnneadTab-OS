__doc__ = "Get the data reading based on the rule from Efficiency schedule, process them and fill to the graphical symbal data calculator on sheets, which shows the workstation seat count, net area and gross area, and what is the efficiency rate of this level."
__title__ = "04.1_efficiency block data filler"
__youtube__ = "https://youtu.be/s8SdKBPqtfs"
from pyrevit import forms, DB, revit, script
import EA_UTILITY
import EnneadTab
import time


def get_update_notice():
    user_name = revit.doc.Application.Username
    localtime = time.asctime( time.localtime(time.time()) ).replace(":","-")
    return user_name, localtime

def rename_schedule():
    key_word = "Script Last Run By "
    all_schedules = DB.FilteredElementCollector(revit.doc).OfClass(DB.ViewSchedule ).WhereElementIsNotElementType().ToElements()
    #print [x.Name for x in all_schedules]
    schedule = filter(lambda x: key_word in x.Name, all_schedules )[0]
    #print [x.Name for x in schedule]

    #check schedule ownership



    #user_name = DB.BasicFileInfo.Username
    user_name, localtime = get_update_notice()
    print(user_name)
    print(localtime)
    new_name = schedule.Name.split(key_word)[0] + key_word + user_name + " at local time " + localtime
    schedule.Name = new_name
    pass

def get_element_level(element):

    #print element.LevelId
    #print revit.doc.GetElement( element.LevelId)
    try:

        level = revit.doc.GetElement( element.LevelId).Name
    except:
        level = 99
        print("cannot find level for {}".format(output.linkify(element.Id)))
    return level

def print_all_para(element):
    print("^"*10)
    for para in element.Parameters:
        #print para.Definition.Name
        if para.Definition.Name == "Workstation Occupancy":
            print("*"*50)
    print("/"*10)

def print_element_link(el):
    print("{}".format(output.linkify(el.Id)))

def get_all_efficiency_data_blocks():
    all_symbol_types =  DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsElementType().ToElements()
    return filter(lambda x: x.Family.Name == "Office Efficiency Calculator", all_symbol_types)


def get_data_block_by_level(level, data_blocks):
    filter(lambda x: x.LookupParameter("Type Name").AsString() == "Office Efficiency Calculator", all_symbol_types)
    pass

def get_all_sgl_workstations():
    primary_option_filter = DB.PrimaryDesignOptionMemberFilter()
    all_furnichures_in_primary_option = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Furniture).WherePasses(primary_option_filter).WhereElementIsNotElementType().ToElements()

    all_furnichures_raw = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Furniture).WhereElementIsNotElementType().ToElements()
    all_furnichures_in_main_model = filter(lambda x: x.DesignOption == None, all_furnichures_raw)

    all_furnichures = list(all_furnichures_in_primary_option) + all_furnichures_in_main_model
    #for x in all_furnichures:
        #print x
        #print_all_para(x.Symbol)
    def is_valid_worksation(x):
        if x.Symbol.LookupParameter("Description").AsString() == "Workstation(1 person)":
            return True
        if x.Symbol.LookupParameter("Description").AsString() == "Hotdesk":
            return True
        return False

    workstation_furnichures = filter(lambda x: x.Symbol.LookupParameter("Workstation Occupancy") != None, all_furnichures)
    single_workstations = filter(lambda x: is_valid_worksation(x), workstation_furnichures)
    return single_workstations

def get_worksation_count_by_level(level):
    global single_workstations
    #print workstation_furnichures
    """
    for x in workstation_furnichures:
        print_element_link(x)
        """
    #print all_furnichures[0]
    #print_all_para(all_furnichures[0])
    #print get_element_level(all_furnichures[0])
    level_workstations = filter(lambda x: get_element_level(x) == level, single_workstations)
    count = 0
    safety = 0


    for furnichure in level_workstations:
        safety += 1
        #print "safety:{}".format(safety)
        if safety > 500000:
            break
        #print furnichure.Symbol#.Name
        #print_all_para(furnichure.Symbol)
        #if hasattr(furnichure.Symbol, "Workstation Occupancy"):
        count += furnichure.Symbol.LookupParameter("Workstation Occupancy").AsInteger()
            #print "found one----------------------"

    #print count
    return count

def get_GFA_area_by_level(level):
    all_areas = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_Areas).WhereElementIsNotElementType().ToElements()
    all_GFAs =  filter(lambda x: x.AreaScheme.Name == "Gross Building" and x.LookupParameter("Area Department").AsString() == "OFFICE", all_areas)
    return filter(lambda x: level == get_element_level(x), all_GFAs)

def get_function_area_by_level(level):

    GFA_in_level = get_GFA_area_by_level(level)


    net_office_area = 0
    core_area = 0
    other_area = 0
    for area in GFA_in_level:
        """
        if level == str(9):
            print(area.LookupParameter("Name").AsString())
            print(EA_UTILITY.sqft_to_sqm(area.Area))
        """
        area_function = area.LookupParameter("Area Layout Function").AsString()
        temp_area = area.Area * area.LookupParameter("MC_$Discount Ratio").AsDouble()

        if area_function == "NET OFFICE":
            net_office_area += temp_area
        elif area_function == "CORE":
            core_area += temp_area
        else:
            other_area += temp_area
    #EA_UTILITY.sqft_to_sqm(x)

    if net_office_area + core_area + other_area == 0:
        print("Level element not found in current file.")
    return net_office_area, core_area, other_area



def set_data_to_data_block(data_block):

    print("*"*20)
    level = data_block.LookupParameter("Type Name").AsString()
    data_block.LookupParameter("level").Set(level)
    print(level)
    workstation_count = get_worksation_count_by_level(level)
    print("workstation count = {}".format(workstation_count))
    data_block.LookupParameter("workstation count").Set(workstation_count)

    def get_placement_count(data_block_type):
        all_generic_annotations = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericAnnotation).WhereElementIsNotElementType().ToElements()
        all_data_block_instances = filter(lambda x: x.Symbol.Family.Name == "Office Efficiency Calculator", all_generic_annotations)
        #print len(all_data_block_instances)
        #print all_data_block_instances[0]
        data_block_instances_of_this_type  = filter(lambda x: x.Symbol.LookupParameter("Type Name").AsString() == data_block_type.LookupParameter("Type Name").AsString(), all_data_block_instances)
        return len(data_block_instances_of_this_type)
    data_block.LookupParameter("placement count").Set(get_placement_count(data_block))

    net_office_area, core_area, other_area = get_function_area_by_level(level)
    print("net_office_area = {}".format(EA_UTILITY.sqft_to_sqm(net_office_area)))
    print("core_area = {}".format(EA_UTILITY.sqft_to_sqm(core_area)))
    print("amenity_area = {}".format(EA_UTILITY.sqft_to_sqm(other_area)))
    data_block.LookupParameter("net office area").Set(net_office_area)
    data_block.LookupParameter("core area").Set(core_area)
    data_block.LookupParameter("amenity area").Set(other_area)

    user_name, localtime = get_update_notice()
    update_note = "info updated by " + user_name + " at local time " + localtime
    data_block.LookupParameter("update note").Set(update_note)

    #sepearte net office, amenity and core
    pass
################## main code below #####################
output = script.get_output()
output.close_others()

single_workstations = get_all_sgl_workstations()

with revit.Transaction("Filler blocks"):
    rename_schedule()
    map(set_data_to_data_block, get_all_efficiency_data_blocks())
