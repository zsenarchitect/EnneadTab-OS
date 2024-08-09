#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Inspect the material keynote, material, subCategory relationship and where there are being used."
__title__ = "42_inspect material keynote, material, family and object style"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def get_sorted_all_materials():
    all_materials = DB.FilteredElementCollector(doc).OfClass(DB.Material).ToElements()

    all_materials = sorted(all_materials, key = lambda x: x.Name)
    return all_materials

def get_sorted_all_appearances():
    all_appearances = DB.FilteredElementCollector(doc).OfClass(DB.AppearanceAssetElement).ToElements()

    all_appearances = sorted(all_appearances, key = lambda x: x.Name)
    return all_appearances


def get_selected_material_keynotes():
    all_materials = list(DB.FilteredElementCollector(doc).OfClass(DB.Material).ToElements())

    keynotes_used = list(set([x.LookupParameter("Keynote").AsString() for x in all_materials]))
    def is_valid_keynote(x):
        if x is None:
            return False
        try:
            if len(x) > 0:
                return True
        except:
            pass
        return False
    keynotes_used = filter(lambda x: is_valid_keynote(x), keynotes_used)
    keynotes_used.sort()
    all_materials.sort(key = lambda x: x.Name)

    selected_keynotes = forms.SelectFromList.show(keynotes_used,
                                                title = ACTION,
                                                multiselect = True)
    return selected_keynotes


def get_obj_styles_by_keynote(keynote, doc = doc):
    temp = []
    categories = doc.Settings.Categories
    for category in categories:
        for sub_c in category.SubCategories:
            if sub_c.Material is None:
                continue
            if sub_c.Material.LookupParameter("Keynote").AsString() == keynote:
                temp.append([category.Name , sub_c.Name, sub_c.Material.Name, sub_c.Material.LookupParameter("Keynote").AsString() ])
    return temp


def get_data_in_all_family():


    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()


    EA_UTILITY.show_toast(message = "This may take a moment or so.", title = "Checking {} families in the background...".format(len(all_families)))


    all_families = sorted(all_families, key = lambda x: x.Name)

    temp = []
    total_count = len(all_families)
    desired_pop_count = 10
    should_pop = False
    target = total_count / float(desired_pop_count)
    for count, family in enumerate(all_families):
        if count > target:
            should_pop = True
        if should_pop:
            EA_UTILITY.show_toast(title = "{} out of {} checked".format(count, total_count))
            should_pop = False
            target += target
        data = inspect_family(family, enable_print = False)
        if data is None or data == []:
            continue
        temp.append([family.Name, data])

    #display_list(temp)
    return temp



def inspect_family(family, enable_print = True):
    if enable_print:
        print("--------")
        print("inspecting family [{}]".format(family.Name))
    temp = []
    try:
        family_doc = doc.EditFamily(family)
    except Exception as e:
        if enable_print:
            print (e)
        return None
    parent_category = family_doc.OwnerFamily.FamilyCategory

    categories = family_doc.Settings.Categories
    for category in categories:
        """
        if category.Name not in [parent_category.Name, "Generic Models"]:
            continue
        """
        for sub_c in category.SubCategories:
            if sub_c.Material is None:
                material_name = ""
                mat_keynote = ""
            else:
                material_name = sub_c.Material.Name
                mat_keynote = sub_c.Material.LookupParameter("Keynote").AsString()

            if sub_c.Material is not None:
                appearance_element = doc.GetElement(sub_c.Material.AppearanceAssetId)
                appearance_name = appearance_element.Name if appearance_element else ""
            else:
                appearance_name = ""

            temp_entry = [category.Name ,
                            sub_c.Name,
                            material_name,
                            mat_keynote,
                            appearance_name ]

            temp.append(temp_entry)
    if enable_print:
        print_detail(temp, prefix = "")
    try:
        family_doc.Close(False)
    except Exception as e:
        print("Family can not be closed becasue:" + e)
    return temp

def print_detail(data_collection, prefix = "", keyword_that_has_to_include = None):
    for x in data_collection:
        #print x
        if keyword_that_has_to_include is None:
            pass
        else:
            if keyword_that_has_to_include not in x:
                continue
        print("{}[{}]--->[{}]--->[{}]--->[{}]--->[{}]".format(prefix, x[0], x[1], x[2], x[3], x[4]))


def check_keynote_in_family(keynote_target, family_data_collection):
    print("------------\nInspecting keynote: {}".format(keynote_target))
    for data in family_data_collection:
        #print "A"
        #print data
        family_name, sub_c_mapping = data
        #print "B"
        #print sub_c_mapping
        for map_entry in sub_c_mapping:
            #print "C"
            #print map_entry
            #print "D"
            #print map_entry[3]
            mat_keynote = map_entry[3]
            if mat_keynote == keynote_target:
                print_detail(sub_c_mapping, prefix = family_name + ": ", keyword_that_has_to_include = mat_keynote)
                print("\n")
                break # break so i dont print same family twice
                # print "{}:{}".format(family_name, map_entry)
    print("\n\n")

def check_appearance_in_family(appearance_target, family_data_collection):
    print("------------\nInspecting Appearance: {}".format(appearance_target))
    for data in family_data_collection:
        #print "A"
        #print data
        family_name, sub_c_mapping = data
        #print "B"
        #print sub_c_mapping
        for map_entry in sub_c_mapping:
            #print "C"
            #print map_entry
            #print "D"
            #print map_entry[3]
            mat_appearance = map_entry[4]
            if mat_appearance == appearance_target:
                print_detail(sub_c_mapping, prefix = family_name + ": ", keyword_that_has_to_include = mat_appearance)
                print("\n")
                break # break so i dont print same family twice
                # print "{}:{}".format(family_name, map_entry)
    print("\n\n")


def check_data_in_family(target, family_data_collection, data_position):
    print("------------\nInspecting: {}".format(target))
    for data in family_data_collection:
        #print "A"
        #print data
        family_name, sub_c_mapping = data
        #print "B"
        #print sub_c_mapping
        for map_entry in sub_c_mapping:
            #print "C"
            #print map_entry
            #print "D"
            #print map_entry[3]
            inspected_item = map_entry[data_position]
            if inspected_item == target:
                print_detail(sub_c_mapping, prefix = family_name + ": ", keyword_that_has_to_include = inspected_item)
                print("\n")
                break # break so i dont print same family twice
                # print "{}:{}".format(family_name, map_entry)
    print("\n\n")


def action_0_inspect_by_family():
    # get all familys to inspect from, select from list
    all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()

    all_families = sorted(all_families, key = lambda x: x.Name)

    all_families = forms.SelectFromList.show(all_families,
                                            name_attr = "Name",
                                            title = ACTION,
                                            multiselect = True)

    global_counter = 0
    limit = len(all_families)
    with forms.ProgressBar(title = "Checking Families, Hold On...({value} of {max_value})", step = 1, cancellable = True) as pb:
    # initiate the class collection.
    	for family in all_families:
    		inspect_family(family)
    		global_counter += 1
    		if pb.cancelled:
    			script.exit()
    		pb.update_progress(global_counter, limit)




def action_2_inspect_keynotes_to_family():
    selected_keynotes = get_selected_material_keynotes()

    all_family_data = get_data_in_all_family()
    #display_list(all_family_data)

    map(lambda x: check_keynote_in_family(x, all_family_data), selected_keynotes)



def action_4_inspect_keynotes_to_OST():
    selected_keynotes = get_selected_material_keynotes()


    for keynote in selected_keynotes:
        print("---------")
        print("inspecting keynote [{}]".format(keynote))
        object_style_display = get_obj_styles_by_keynote(keynote)
        display_list(object_style_display)
        print("\n\n")


def action_5_insepect_keynotes():
    selected_keynotes = get_selected_material_keynotes()
    all_materials = get_sorted_all_materials()

    for keynote in selected_keynotes:
        print("---------")
        print("checking keynote usage of {}".format(keynote))
        for material in all_materials:
            if material.LookupParameter("Keynote").AsString() == keynote:
                print("--[{}]".format(material.Name))
        print("\n\n")


def action_6_inspect_materials():

    all_materials = get_sorted_all_materials()
    selected_materials = forms.SelectFromList.show(all_materials,
                                                name_attr = "Name",
                                                title = ACTION,
                                                multiselect = True)

    for mat in selected_materials:
        print("[{}]--->[{}]".format(mat.Name, mat.LookupParameter("Keynote").AsString()))

def action_8_inspect_mat_to_appearance():

    all_materials = get_sorted_all_materials()
    selected_materials = forms.SelectFromList.show(all_materials,
                                                name_attr = "Name",
                                                title = ACTION,
                                                multiselect = True)

    for mat in selected_materials:
        appearance_element = doc.GetElement(mat.AppearanceAssetId)
        appearance_name = appearance_element.Name if appearance_element else ""
        print("[{}]--->[{}]".format(mat.Name, appearance_name))

def action_7_inspect_appearance():

    all_appearances = get_sorted_all_appearances()
    selected_appearances = forms.SelectFromList.show(all_appearances,
                                                name_attr = "Name",
                                                title = ACTION,
                                                multiselect = True)

    all_family_data = get_data_in_all_family()

    map(lambda x: check_appearance_in_family(x.Name, all_family_data), selected_appearances)
    """
    for appearance in selected_appearances:
        print("_"*10)
        print(appearance.Name)
        #print "[{}]--->[{}]".format(appearance.Name, appearance.LookupParameter("Keynote").AsString())
    """

def action_3_inspect_mat_to_family():

    all_materials = get_sorted_all_materials()
    selected_materials = forms.SelectFromList.show(all_materials,
                                                name_attr = "Name",
                                                title = ACTION,
                                                multiselect = True)

    all_family_data = get_data_in_all_family()

    map(lambda x: check_data_in_family(x.Name, all_family_data, data_position = 2), selected_materials)

def action_9_export_map_OST_to_material():
    def get_rhino_material_name(revit_material_name):
        if EA_UTILITY.string_contain_keywords(revit_material_name, ["glass"]):
            return rhino_mat_name_glass(revit_material_name)

        if EA_UTILITY.string_contain_keywords(revit_material_name, ["stone"]):
            return rhino_mat_name_stone(revit_material_name)

        if EA_UTILITY.string_contain_keywords(revit_material_name, ["mullion", "metal"]):
            return rhino_mat_name_metal(revit_material_name)

        return revit_material_name

    def rhino_mat_name_stone(revit_material_name):
        return revit_material_name

    def rhino_mat_name_metal(revit_material_name):
        revit_material_name = revit_material_name.replace("Accent Metal", "Metal Accent")
        revit_material_name = revit_material_name.replace("Dark Metal", "Metal Dark")
        revit_material_name = revit_material_name.replace("White Metal", "Metal White")
        return revit_material_name

    def rhino_mat_name_glass(revit_material_name):
            """glass type"""
            if EA_UTILITY.string_contain_keywords(revit_material_name, ["cable wall", "railing", "retail", "storefront"]):
            #if "cable wall" in revit_material_name.lower() or "railing" in revit_material_name.lower() or "retail" in revit_material_name.lower():
                return "2135_Glass Clear"

            if "sphere" in revit_material_name.lower():
                return "2135_Glass Sphere"

            if "tower" in revit_material_name.lower():
                return "2135_Glass Tower"

            return "2135_Glass Standard"

    map = []
    categories = doc.Settings.Categories
    for category in categories:
        if "Imports in Families" in category.Name or ".dwg" in category.Name:
            continue

        layer_name = "{}".format(category.Name)
        if category.Material is None:
            revit_material_name = "None"
        else:
            revit_material_name = category.Material.Name
        rhino_material_name = get_rhino_material_name(revit_material_name)
        map.append( (layer_name, revit_material_name, rhino_material_name))
        for sub_c in category.SubCategories:
            layer_name = "{}_{}".format(category.Name, sub_c.Name)
            if sub_c.Material is None:
                revit_material_name = "None"
            else:
                revit_material_name = sub_c.Material.Name
            rhino_material_name = get_rhino_material_name(revit_material_name)
            map.append( (layer_name, revit_material_name, rhino_material_name))

    OUT = []
    map.sort(key = lambda x: x[0])
    unique_rhino_mat_names = set()
    for data in map:

        layer_name, revit_material_name, rhino_material_name = data
        data = "{}-->{}-->{}".format(layer_name, revit_material_name, rhino_material_name)
        unique_rhino_mat_names.add(rhino_material_name)
        print(data)
        OUT.append(data)
    output.print_md( "Format explain ***Layer Name/ Object Style-->Revit Material Name-->Mapped Rhino Material Name***")

    unique_rhino_mat_names = sorted(list(unique_rhino_mat_names))
    print("\n\n")
    output.print_md("**Unique Rhino Material Names below.**")
    for x in unique_rhino_mat_names:
        print(x)



    filepath = r"I:\2135\0_BIM\10_BIM Management\10_BIM Resources\ost material mapping\ost material mapping_{}.txt".format(doc.Title)
    EA_UTILITY.save_list_to_txt(OUT, filepath, use_encode = True)

    filepath = r"I:\2135\0_3D\03_Working Models\##Master Shared_Rhino materials\Unique Rhino Material Usage\###Unique Rhino Material_{}.txt".format(doc.Title)
    EA_UTILITY.save_list_to_txt(unique_rhino_mat_names, filepath, use_encode = True)

def display_list(list):
    for x in list:
        print("--{}".format(x))


################## main code below #####################
output = script.get_output()
output.close_others()
#ideas:
options = ["family--->[object styles--->material--->keynotes--->appearance]",
            "object styles---> family  (will consider adding function if get enough request)",
            "keynotes---> family",
            "materials---> family",
            "keynotes---> [object styles --->material--->keynotes]",
            "keynotes---> materials",
            "materials---> keynotes",
            "appearance---> family",
            "materials---> appearance",
            "Export Map: objects styles-->material"]
ACTION = forms.SelectFromList.show(options,
                                title = "what do you want to do? Inspection workflow below",
                                multiselect = False)

if ACTION is None:
    script.exit()
output.set_title(ACTION)

if ACTION == options[0]:
    action_0_inspect_by_family()
if ACTION == options[2]:
    action_2_inspect_keynotes_to_family()
if ACTION == options[3]:
    action_3_inspect_mat_to_family()
if ACTION == options[4]:
    action_4_inspect_keynotes_to_OST()
if ACTION == options[5]:
    action_5_insepect_keynotes()
if ACTION == options[6]:
    action_6_inspect_materials()
if ACTION == options[7]:
    action_7_inspect_appearance()
if ACTION == options[8]:
    action_8_inspect_mat_to_appearance()
output.freeze()
if ACTION == options[9]:
    action_9_export_map_OST_to_material()

output.unfreeze()
print("\n\n-------------inspection finished")
