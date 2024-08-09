#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Legacy, now in Output panel"
__title__ = "47_Isolate export type for Wall/Floor/Roof/Column/Stair(Legacy)"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
import time
from Autodesk.Revit import DB # pyright: ignore 
import traceback
uidoc = __revit__.ActiveUIDocument
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

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
        print(current_name)
        print(new_name)
        print (e)
        EA_UTILITY.dialogue(main_text = "'\ : { } [ ] | ; < > ? ` ~' are not allowed in view name for Revit or Window OS.If you are exporting from default Revit 3D view, it will comes with '{}' in the view name which can casue error for window file naming.\nPlease rename your view first, just remove '{}'.", sub_text = "Original view name = {}\nError message: ".format(current_name) + str(e) + "\nSuggested new name = {}".format(current_name.replace("{", "").replace("}", "")))


def isolate_elements_temporarily(element_ids):
    doc.ActiveView.IsolateElementsTemporary(EA_UTILITY.list_to_system_list(element_ids))
    pass


def process_type(type):
    type_name = type.LookupParameter("Type Name").AsString()
    if type.Category.Name == "Walls":
        elements = get_wall_elements_ids(type)
        file_name = "WallType_{}".format(type_name)
    elif type.Category.Name == "Floors":
        elements = get_floor_elements_ids(type)
        file_name = "FloorType_{}".format(type_name)
    elif type.Category.Name == "Roofs":
        elements = get_roof_elements_ids(type)
        file_name = "RoofType_{}".format(type_name)
    elif "Column" in type.Category.Name:
        elements = get_column_elements_ids(type)
        file_name = "ColumnType_{}".format(type_name)
    elif type.Category.Name == "Stairs":
        elements = get_stair_elements_ids(type)
        file_name = "StairType_{}".format(type_name)
    else:
        print("unknown type = " + type_name)
        return

    if len(elements) == 0:
        print("None found in this view.")
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

def get_wall_elements_ids(wall_type):
    print("----"*5)
    wall_type_name = wall_type.LookupParameter("Type Name").AsString()
    print("processing walltype [{}]".format(wall_type_name))
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

    def get_element_ids_on_wall(wall):
        return list(wall.GetDependentElements(None))
        curtain_grid = wall.CurtainGrid
        panel_ids = list(curtain_grid.GetPanelIds())
        #print panel_ids
        return panel_ids


    wall_ids = [x.Id for x in my_walls]
    #uidoc.Selection.SetElementIds (EA_UTILITY.list_to_system_list(wall_ids))
    for wall in my_walls:
        wall_ids.extend(get_element_ids_on_wall(wall))

    return wall_ids

def get_floor_elements_ids(floor_type):

    print("----"*5)
    floor_type_name = floor_type.LookupParameter("Type Name").AsString()
    print("processing floortype [{}]".format(floor_type_name))

    #all_floors = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
    all_floors = get_elements_by_OST(DB.BuiltInCategory.OST_Floors)
    my_floors = filter(lambda x: x.FloorType.LookupParameter("Type Name").AsString() == floor_type_name, all_floors  )

    floor_ids = [x.Id for x in my_floors]
    return floor_ids

def get_roof_elements_ids(roof_type):

    print("----"*5)
    roof_type_name = roof_type.LookupParameter("Type Name").AsString()
    print("processing rooftype [{}]".format(roof_type_name))

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

    print("----"*5)
    column_type_name = column_type.LookupParameter("Type Name").AsString()
    print("processing columntype [{}]".format(column_type_name))

    #all_archi_columns = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Columns).WhereElementIsNotElementType().ToElements()
    all_archi_columns = get_elements_by_OST(DB.BuiltInCategory.OST_Columns)
    #all_structral_columns = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElements()
    all_structral_columns = get_elements_by_OST(DB.BuiltInCategory.OST_StructuralColumns)
    all_columns = list(all_archi_columns) + list(all_structral_columns)
    my_columns = filter(lambda x: x.Symbol.LookupParameter("Type Name").AsString() == column_type_name, all_columns)

    column_ids = [x.Id for x in my_columns]
    return column_ids

def get_stair_elements_ids(stair_type):

    print("----"*5)
    stair_type_name = stair_type.LookupParameter("Type Name").AsString()
    print("processing stairtype [{}]".format(stair_type_name))



    #all_stairs = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Stairs).WhereElementIsNotElementType().ToElements()
    all_stairs = get_elements_by_OST(DB.BuiltInCategory.OST_Stairs)
    my_stairs = filter(lambda x: doc.GetElement(x.GetTypeId()).LookupParameter("Type Name").AsString()  == stair_type_name, all_stairs  )

    stair_ids = [x.Id for x in my_stairs]
    for stair in my_stairs:
        stair_ids.extend(stair.GetAssociatedRailings ())
        stair_ids.extend(stair.GetDependentElements(None))
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

def export_dwg_action(file_name, view_or_sheet, doc, output_folder, additional_msg = ""):
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

    EA_UTILITY.show_toast(app_name = "Bilibili exporter",
                            title = "[{}.dwg] saved.".format(file_name),
                            image = "C:\Users\szhang\github\EnneadTab 2.0\ENNEAD.extension\Ennead.tab\Tailor Shop.panel\misc1.stack\Proj 2135.pulldown\icon.png",
                            message = additional_msg)


def OLD_process_wall_type(wall_type):
    print("----"*5)
    wall_type_name = wall_type.LookupParameter("Type Name").AsString()
    print("processing walltype [{}]".format(type_name))
    # get walls instance of this type in current view
    all_walls = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
    my_walls = filter(lambda x: x.WallType.LookupParameter("Type Name").AsString() == wall_type.LookupParameter("Type Name").AsString(), all_walls  )
    #print my_walls
    #print len(my_walls)

    def get_element_ids_on_wall(wall):
        return list(wall.GetDependentElements(None))
        curtain_grid = wall.CurtainGrid
        panel_ids = list(curtain_grid.GetPanelIds())
        #print panel_ids
        return panel_ids


    wall_ids = [x.Id for x in my_walls]
    #uidoc.Selection.SetElementIds (EA_UTILITY.list_to_system_list(wall_ids))
    for wall in my_walls:
        wall_ids.extend(get_element_ids_on_wall(wall))

    #print wall_ids
    isolate_elements_temporarily(wall_ids)
    file_name = "WalType_{}".format(wall_type_name)
    export_dwg_action(file_name, doc.ActiveView, doc, OUTPUT_FOLDER)
    #restore_view
    doc.ActiveView.DisableTemporaryViewMode (DB.TemporaryViewMode.TemporaryHideIsolate)
    pass

def get_elements_by_OST(OST):
    filter = DB.PrimaryDesignOptionMemberFilter()
    all_els_in_primary_options = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(OST).WherePasses(filter).ToElements()
    print ("{} primary design option items".format(len(all_els_in_primary_options)))
    all_els = DB.FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(OST).WhereElementIsNotElementType().ToElements()
    all_els = list(all_els)
    all_els.extend(all_els_in_primary_options)
    return all_els



################## main code below #####################
output = script.get_output()
output.close_others()
if any([doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .RevealHiddenElements),
        doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .TemporaryHideIsolate),
        doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .WorksharingDisplay),
        doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .TemporaryViewProperties),
        doc.ActiveView.IsInTemporaryViewMode (DB.TemporaryViewMode .RevealConstraints)]):
    EA_UTILITY.dialogue(main_text = "Cannot use temporary view mode for this tool. You can apply changes to make it permanent before proceeding.")
    script.exit()
#ideas:

# get all walltypes in file
all_wall_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()
all_floor_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Floors).WhereElementIsElementType().ToElements()
all_roof_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Roofs).WhereElementIsElementType().ToElements()
all_column_types = list(DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Columns).WhereElementIsElementType().ToElements())
all_column_types.extend( DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_StructuralColumns).WhereElementIsElementType().ToElements())
all_stair_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Stairs).WhereElementIsElementType().ToElements()
all_types = list(all_wall_types) + list(all_floor_types) + list(all_roof_types) + list(all_column_types) + list(all_stair_types)

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

ops = [MyOption(x) for x in all_types]
#print "type ready"
ops.sort(key = lambda x: x.name)
selected_types = forms.SelectFromList.show(ops,
                                            multiselect = True)

if not selected_types:
    script.exit()


DWG_export_setting = get_export_setting(doc, setting_name = "Empty")
DWG_option = DB.DWGExportOptions().GetPredefinedOptions(doc, DWG_export_setting.Name)
OUTPUT_FOLDER = forms.pick_folder(title = "folder for the output DWG, best if you can create a empty folder")
#print selected_walltypes
# for each waltype, get wall, its hosted elements, isolated temp, export, restore view.
T = DB.TransactionGroup(doc, "export by type")
T.Start()
update_view_name()
map(process_type, selected_types)
T.Commit()
