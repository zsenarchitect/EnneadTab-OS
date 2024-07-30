#!/usr/bin/python
# -*- coding: utf-8 -*-

# !!!!!!!!!for future: process the other category that is not system family
# get a long list of other categories that support loadable family,  they can have similar export  api workflow

__doc__ = "Pick category and type for the dwg export. It will isolate elements by types in the view and give individual .dwg file.\n\nThe child elements such as shared family will be isolated as well.\n\nUse EnneadTab for Rhino <Import Revit Export Collection> to get things under type parent layers.\n\nCurrently handle Wall/Floor/Roof/Column/Stair\n\nThis tool primarily deal with the system family category that normally will be difficult to seperate in dwg export."
__title__ = "Isolated Export\nBy System Family Type"
__tip__ = True
__youtube__ = "https://youtu.be/o_cnp-BvnHw"
import os
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import DATA_FILE, NOTIFICATION, DATA_CONVERSION, ERROR_HANDLE, LOG, FOLDER
import time

from Autodesk.Revit import DB # pyright: ignore 
import traceback
import sys
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

def update_view_name():
    current_name = doc.ActiveView.Name

    keyword = ", exported by "
    user_time = EA_UTILITY.get_formatted_current_time()
    if keyword not in current_name:
        new_name = current_name + keyword + user_time
    else:
        new_name = current_name.split(keyword)[0] + keyword + user_time

    new_name = new_name.replace(":", "-")
    new_name = new_name.replace("{", "")
    new_name = new_name.replace("}", "")
    #print new_name
    try:
        t = DB.Transaction(doc, "temp view rename")
        t.Start()
        doc.ActiveView.Name = new_name
        doc.Regenerate ()
        t.Commit()
        #print "new name set"
    except Exception as e:
        print (current_name)
        print (new_name)
        print (e)
        REVIT_FORMS.dialogue(main_text = "'\ : { } [ ] | ; < > ? ` ~' are not allowed in view name for Revit or Window OS.If you are exporting from default Revit 3D view, it will comes with '{}' in the view name which can casue error for window file naming.\nPlease rename your view first, just remove '{}'.", sub_text = "Original view name = {}\nError message: ".format(current_name) + str(e) + "\nSuggested new name = {}".format(current_name.replace("{", "").replace("}", "")))


def isolate_elements_temporarily(element_ids):
    if IS_FROM_LINK:
        everythings = DB.FilteredElementCollector(doc, doc.ActiveView.Id).WhereElementIsNotElementType ().ToElements()

        for e in everythings:
            if isinstance(e, DB.RevitLinkInstance ):
                if e.GetLinkDocument().Title == export_doc.Title:
                    doc.ActiveView.IsolateElementsTemporary(DATA_CONVERSION.list_to_system_list([e.Id]))
                    # now that the link instance is here, i am going to hide everything tht is not in keeping lst
                    break



        everything_in_link = DB.FilteredElementCollector(export_doc).WhereElementIsNotElementType ().ToElements()
        bad_types = set()
        for e in everything_in_link:
            if e.Id not in element_ids:
                try:
                    # bad performance......i am not using batch hide becasue there are som etype cannot be hidden, and there is no( yet) easy way to find which can hide or not... so just treat them individually
                    doc.ActiveView.HideElements (DATA_CONVERSION.list_to_system_list([e.Id]))
                except:
                    # print ("cannot hide {}".format(type(e)))
                    bad_types.add(type(e))
                    pass
        for bad_type in bad_types:
            print ("cannot hide {}".format(bad_type))
        return
    doc.ActiveView.IsolateElementsTemporary(DATA_CONVERSION.list_to_system_list(element_ids))
    pass


def process_type(revit_type):

    global OUTPUT_FOLDER
    type_name = revit_type.LookupParameter("Type Name").AsString()
    if revit_type.Category.Name == "Walls":
        elements = get_wall_elements_ids(revit_type)
        file_name = "WallType_{}".format(type_name)
    elif revit_type.Category.Name == "Floors":
        elements = get_floor_elements_ids(revit_type)
        file_name = "FloorType_{}".format(type_name)
    elif revit_type.Category.Name == "Roofs":
        elements = get_roof_elements_ids(revit_type)
        file_name = "RoofType_{}".format(type_name)
    elif "Column" in revit_type.Category.Name:
        elements = get_column_elements_ids(revit_type)
        file_name = "ColumnType_{}".format(type_name)
    elif revit_type.Category.Name == "Stairs":
        elements = get_stair_elements_ids(revit_type)
        file_name = "StairType_{}".format(type_name)
    else:
        elements = get_fam_ins_ids(revit_type)
        file_name = "{}Type_[{}] {}".format(revit_type.Family.FamilyCategory.Name,
                                            revit_type.FamilyName,
                                            type_name)

        

    if len(elements) == 0:
        print ("None found in this view.")
        return

    """
    new method
    """

    #T = DB.TransactionGroup(doc, "temp_action")
    #T.Start()
    t = DB.Transaction(doc, "make view")
    t.Start()
    isolate_elements_temporarily(elements)

    doc.ActiveView.ConvertTemporaryHideIsolateToPermanent()
    export_dwg_action(file_name, doc.ActiveView, doc, OUTPUT_FOLDER)
    #T.RollBack()
    t.RollBack()
    return



    """
    original method
    """

    isolate_elements_temporarily(elements)
    export_dwg_action(file_name, doc.ActiveView, doc, OUTPUT_FOLDER)
    doc.ActiveView.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate)
    pass

def get_fam_ins_ids(symbol):
    print ("----"*5)
    type_name = symbol.LookupParameter("Type Name").AsString()
    print ("processing {} <{}>[{}]".format(symbol.Family.FamilyCategory.Name,
                                          symbol.FamilyName,
                                            type_name))
    
    
    # cate_filter = DB.ElementCategoryFilter()
    option_filter = DB.PrimaryDesignOptionMemberFilter()
    all_els_in_primary_options = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategoryId(symbol.Family.FamilyCategoryId).WherePasses(option_filter).ToElements()
    print ("{} primary design option items".format(len(all_els_in_primary_options)))
    all_els = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategoryId(symbol.Family.FamilyCategoryId).WhereElementIsNotElementType().ToElements()
    all_els = list(all_els)
    all_els.extend(all_els_in_primary_options)
    
    
    my_els = filter(lambda x: hasattr(x, "Symbol") and x.Symbol.LookupParameter("Type Name").AsString() == type_name, all_els  )

    return [x.Id for x in my_els]



def get_wall_elements_ids(wall_type):
    print ("----"*5)
    wall_type_name = wall_type.LookupParameter("Type Name").AsString()
    print ("processing walltype [{}]".format(wall_type_name))
    # get walls instance of this type in current view
    all_walls = get_elements_by_OST(DB.BuiltInCategory.OST_Walls)
    #all_walls = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    def get_type_name(x):
        if hasattr(x, "WallType"):
            return x.WallType.LookupParameter("Type Name").AsString()
        #print "##"
        #print x.Name
        return x.Name
    my_walls = filter(lambda x: get_type_name(x) == wall_type_name, all_walls  )
    #print my_walls
    #print len(my_walls)

    def is_wall_related(x):
        element = doc.GetElement(x)
        if not element.Category:
            return False
        if element.Category.Name in ["Windows", "Doors"]:
            return False
        return True
    def get_element_ids_on_wall(wall):
        return list(wall.GetDependentElements(None))
        return filter(is_wall_related , wall.GetDependentElements(None))
        curtain_grid = wall.CurtainGrid
        panel_ids = list(curtain_grid.GetPanelIds())
        #print panel_ids
        return panel_ids


    wall_ids = [x.Id for x in my_walls]

    #uidoc.Selection.SetElementIds (DATA_CONVERSION.list_to_system_list(wall_ids))
    for wall in my_walls:
        wall_ids.extend(get_element_ids_on_wall(wall))

    return wall_ids

def get_floor_elements_ids(floor_type):

    print ("----"*5)
    floor_type_name = floor_type.LookupParameter("Type Name").AsString()
    print ("processing floortype [{}]".format(floor_type_name))

    #all_floors = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
    all_floors = get_elements_by_OST(DB.BuiltInCategory.OST_Floors)
    my_floors = filter(lambda x: x.FloorType.LookupParameter("Type Name").AsString() == floor_type_name, all_floors  )

    floor_ids = [x.Id for x in my_floors]
    return floor_ids

def get_roof_elements_ids(roof_type):

    print ("----"*5)
    roof_type_name = roof_type.LookupParameter("Type Name").AsString()
    print ("processing rooftype [{}]".format(roof_type_name))

    #all_roofs = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Roofs).WhereElementIsNotElementType().ToElements()
    all_roofs = get_elements_by_OST(DB.BuiltInCategory.OST_Roofs)
    def get_roof_type_name(x):
        if hasattr(x, "RoofType"):
            return x.RoofType.LookupParameter("Type Name").AsString()
        return x.Name
    my_roofs = filter(lambda x: get_roof_type_name(x) == roof_type_name, all_roofs  )

    roof_ids = [x.Id for x in my_roofs]
    return roof_ids

def get_column_elements_ids(column_type):

    print ("----"*5)
    column_type_name = column_type.LookupParameter("Type Name").AsString()
    print ("processing columntype [{}]".format(column_type_name))

    #all_archi_columns = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()
    all_archi_columns = get_elements_by_OST(DB.BuiltInCategory.OST_Columns)
    #all_structral_columns = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements()
    all_structral_columns = get_elements_by_OST(DB.BuiltInCategory.OST_StructuralColumns)
    all_columns = list(all_archi_columns) + list(all_structral_columns)
    my_columns = filter(lambda x: x.Symbol.LookupParameter("Type Name").AsString() == column_type_name, all_columns)

    column_ids = [x.Id for x in my_columns]
    return column_ids

def get_stair_elements_ids(stair_type):

    print ("----"*5)
    stair_type_name = stair_type.LookupParameter("Type Name").AsString()
    print ("processing stairtype [{}]".format(stair_type_name))



    #all_stairs = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()
    all_stairs = get_elements_by_OST(DB.BuiltInCategory.OST_Stairs)
    my_stairs = filter(lambda x: doc.GetElement(x.GetTypeId()).LookupParameter("Type Name").AsString()  == stair_type_name, all_stairs  )

    stair_ids = [x.Id for x in my_stairs]
    for stair in my_stairs:
        if isinstance(stair, DB.FamilyInstance):
            if stair.Symbol.Family.IsInPlace:
                print ("!!!!! stairtype [{}] is a in-place family.".format(stair_type_name))
                NOTIFICATION.messenger(main_text = "<{}> is a in-place family".format(stair_type_name))
                
        try:
            stair_ids.extend(stair.GetAssociatedRailings ())
        except:
            NOTIFICATION.messenger(main_text = "<{}> has no associated railings".format(stair_type_name))
            
        try:
            stair_ids.extend(stair.GetDependentElements(None))
        except:
            NOTIFICATION.messenger(main_text = "<{}> has no dependent elements".format(stair_type_name))

    return stair_ids




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
                                                    button_name='use setting with this name for this export job', \
                                                    title = "Select existing Export Setting.")
            if sel_setting == None:
                REVIT_FORMS.dialogue(main_text = "You didn't select any export setting. Try again.")
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
            REVIT_FORMS.dialogue(main_text = "Cannot find setting with same name to match [{}], please manual select".format(setting_name))
            sel_setting = pick_from_setting()


    return sel_setting

def export_dwg_action(file_name, view_or_sheet, doc, output_folder, additional_msg = ""):
    global DWG_option

    time_start = time.time()
    if r"/" in file_name:
        file_name = file_name.replace("/", "-")
        print ("Windows file name cannot contain '/' in its name, i will replace it with '-'")
    if "\"" in file_name:
        file_name = file_name.replace("\"", "in")
        print ("Windows file name cannot contain '\"' in its name, i will replace it with 'in'")
    if "'" in file_name:
        file_name = file_name.replace("'", "in")
        print ("Windows file name cannot contain '\'' in its name, i will replace it with 'ft'")
        
        
        
    print ("preparing [{}].dwg".format(file_name))
    _path = os.path.join(output_folder, file_name + ".dwg")
    if os.path.exists(_path):
        os.remove(_path)
    
    view_as_collection = DATA_CONVERSION.list_to_system_list([view_or_sheet.Id])
    max_attempt = 10
    attempt = 0
    #print view_as_collection
    #print view_or_sheet
    while True:
        if attempt > max_attempt:
            print  ("Give up on <{}>, too many failed attempts, see reason above.".format(file_name))
            break
        attempt += 1
        try:
            doc.Export(output_folder, r"{}".format(file_name), view_as_collection, DWG_option)
            print ("DWG export succesfully")
            break
        except Exception as e:
            if  "The files already exist!" in e:
                file_name = file_name + "_same name"
                #new_name = print_manager.PrintToFileName = r"{}\{}.pdf".format(output_folder, file_name)
                output.print_md("------**There is a file existing with same name, will attempt to save as {}**".format(file_name))

            else:
                if "no views/sheets selected" in e:
                    print (e)
               
                    has_non_print_sheet = True
                else:
                    print (e)

    time_end = time.time()
    additional_msg = "exporting DWG takes {}s".format( time_end - time_start)
    print( additional_msg)
    _path = os.path.join(output_folder, file_name + ".pcp")
    if os.path.exists(_path):
        os.remove(_path)


    NOTIFICATION.messenger("[{}.dwg] saved.".format(file_name) + additional_msg)


def get_elements_by_OST(OST):
    filter = DB.PrimaryDesignOptionMemberFilter()
    if IS_FROM_LINK:
        all_els_in_primary_options = DB.FilteredElementCollector(export_doc).OfCategory(OST).WherePasses(filter).ToElements()
    else:
        all_els_in_primary_options = DB.FilteredElementCollector(export_doc, doc.ActiveView.Id).OfCategory(OST).WherePasses(filter).ToElements()
    print ("{} primary design option items".format(len(all_els_in_primary_options)))
    if IS_FROM_LINK:
        all_els = DB.FilteredElementCollector(export_doc).OfCategory(OST).WhereElementIsNotElementType().ToElements()
    else:
        all_els = DB.FilteredElementCollector(export_doc, doc.ActiveView.Id).OfCategory(OST).WhereElementIsNotElementType().ToElements()
    all_els = list(all_els)
    all_els.extend(all_els_in_primary_options)
    print ("totally found {} items".format(len(all_els)))
    return all_els

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    if any([doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .RevealHiddenElements),
            doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .TemporaryHideIsolate),
            doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .WorksharingDisplay),
            doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .TemporaryViewProperties),
            doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .RevealConstraints)]):
        REVIT_FORMS.dialogue(main_text = "Cannot use temporary view mode for this tool. You can apply changes to make it permanent before proceeding.")
        return
    #ideas:

    # get all walltypes in file
    def is_good(x):
        if x.Family.FamilyPlacementType in [DB.FamilyPlacementType.ViewBased,
                                              DB.FamilyPlacementType.CurveBasedDetail]:
            return False
        if x.Family.FamilyCategory .Name in ["Curtain Panels",
                                             "Curtain Wall Mullions",
                                             "Doors",
                                             "Windows",
                                             "Balusters"]:
            return False
        
        return True
    
    all_fam_ins_types = DB.FilteredElementCollector(doc).OfClass(DB.FamilySymbol).ToElements()
    all_fam_ins_types = filter(is_good, 
                               all_fam_ins_types)
    
    
    all_wall_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
    all_floor_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
    all_roof_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Roofs).WhereElementIsElementType().ToElements()
    all_column_types = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Columns).WhereElementIsElementType().ToElements())
    all_column_types.extend( DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_StructuralColumns).WhereElementIsElementType().ToElements())
    all_stair_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Stairs).WhereElementIsElementType().ToElements()
    all_types = list(all_wall_types) + list(all_floor_types) + list(all_roof_types) + list(all_column_types) + list(all_stair_types) + list(all_fam_ins_types)

    """
    for x in all_types:
        print(x.Category.Name)
    """


    class MyOption(forms.TemplateListItem):
        @property
        def name(self):

            def get_family_by_name(name):
                all_families = DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements()
                family = filter(lambda x: x.Name == name, all_families)
                #print all_families[0].Name
                if family is not None:
                    #print "$$"
                    #print family
                    return family[0]
                return None



            if self.item.Category.Name == "Walls":
                if hasattr(self.item, "Kind"):
                    wall_kind = self.item.Kind
                    if "basic" in str(wall_kind).lower():
                        wall_kind = "Basic"
                    else:
                        wall_kind = "Curtain"
                    return "[Wall {}]:{}".format(wall_kind, self.item.LookupParameter("Type Name").AsString())
                return "[Wall In-Place]:{}".format(self.item.LookupParameter("Type Name").AsString())
            if self.item.Category.Name == "Floors":
                return "[Floor]:{}".format( self.item.LookupParameter("Type Name").AsString())
            if self.item.Category.Name == "Roofs":
                if not hasattr(self.item, "FamilyName"):
                    return "[Roof]:{}".format( self.item.LookupParameter("Type Name").AsString())
                if self.item.FamilyName in ["Basic Roof", "Sloped Glazing", "Fascia", "Gutter", "Roof Soffit"]:
                    roof_kind = self.item.FamilyName
                    if "basic" in roof_kind.lower():
                        roof_kind = "Basic"
                    if "soffit" in roof_kind.lower():
                        roof_kind = "Soffit"

                    return "[Roof {}]:{}".format( roof_kind, self.item.LookupParameter("Type Name").AsString())

                try:
                    family = get_family_by_name(self.item.FamilyName)
                    if family.IsInPlace:
                        return "[Roof In-Place]:[{}]{}".format(self.item.FamilyName, self.item.LookupParameter("Type Name").AsString())
                except Exception as e:
                    print (traceback.format_exc())
                    return "[Roof]:{}".format( self.item.LookupParameter("Type Name").AsString())

            if "Column" in self.item.Category.Name:
                return "[Column]:{}".format( self.item.LookupParameter("Type Name").AsString())
            if self.item.Category.Name == "Stairs":
                return "[Stair]:{}".format( self.item.LookupParameter("Type Name").AsString())
            
            return "[{}]:<{}> {}".format( self.item.Category.Name, 
                                         self.FamilyName,
                                         self.item.LookupParameter("Type Name").AsString())

    ops = [MyOption(x) for x in all_types]
    #print "type ready"
    ops.sort(key = lambda x: x.name)
    selected_types = forms.SelectFromList.show(ops,
                                                multiselect = True,
                                                title = "Pick types that you want to export.")

    if not selected_types:
        return


    global DWG_option
    global OUTPUT_FOLDER
    DWG_export_setting = get_export_setting(doc, setting_name = "Empty")
    if not DWG_export_setting:
        return
    DWG_option = DB.DWGExportOptions().GetPredefinedOptions(doc, DWG_export_setting.Name)
    OUTPUT_FOLDER = forms.pick_folder(title = "folder for the output DWG, best if you can create a empty folder")
    if not OUTPUT_FOLDER:
        return
    #print selected_walltypes
    # for each waltype, get wall, its hosted elements, isolated temp, export, restore view.
    T = DB.TransactionGroup(doc, "export by type")
    T.Start()
    update_view_name()
    map(process_type, selected_types)
    T.Commit()
    
    export_ost_material_map()
    print ("\n\nTool Finished!")
    NOTIFICATION.messenger("All exported!")
    
    
def export_ost_material_map():
    material_map = {}
    # get all the category
    all_cates = doc.Settings.Categories
    for cate in all_cates:
        for sub_c in cate.SubCategories:
            material = sub_c.Material
            if not material:
                continue
            material_data = {}
            material_data["name"] = material.Name
            R, G, B = int(material.Color.Red), int(material.Color.Green), int(material.Color.Blue)
            material_data["color"] = {"diffuse": [R, G, B],
                                       "transparency": int(material.Transparency),
                                       "shininess": int(material.Shininess)}
            material_map[sub_c.Name] = material_data
    DATA_FILE.set_data(material_map, "EA_OST_MATERIAL_MAP.sexyDuck", True)
    
################## main code below #####################
output = script.get_output()
output.close_others()
if __name__ == "__main__":
    links = REVIT_APPLICATION.get_revit_link_docs(link_only=True)
    if False and len(links) > 0: # giveup on exprt from link becasue you cannot isolate the elelments from links...unless use dynamic view filter, but that is too painful and bring little benifit.
        export_doc = REVIT_APPLICATION.select_revit_link_docs(select_multiple = False, including_current_doc = True, link_only = False)
        IS_FROM_LINK = True
    else:
        export_doc = doc
        IS_FROM_LINK = False
    main()
    
