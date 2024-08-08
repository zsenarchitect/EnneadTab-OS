#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Legacy, now under family panel"
__title__ = "79_map_instance_property(legacy)"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
from pyrevit.coreutils import envvars


def process_instance_recording(instance):
    print("###############")
    print(instance)
    print(instance.UniqueId)
    data_entry_pack = []
    for para in instance.Parameters:
        definition = para.Definition
        print(definition.Name)
        #print para.StorageType
        if para.StorageType == DB.StorageType.Integer:
            #print para.AsInteger()
            data_entry = (definition.Name, "int", para.AsInteger())
        if para.StorageType == DB.StorageType.Double:
            #print para.AsDouble()
            data_entry = (definition.Name, "dbl", para.AsDouble())
        if para.StorageType == DB.StorageType.String:
            #print para.AsString()
            data_entry = (definition.Name, "str", para.AsString())
        if para.StorageType == DB.StorageType.ElementId:
            #print para.AsElementId()
            data_entry = (definition.Name, "id", para.AsElementId())

        data_entry_pack.append(data_entry)

    global DATA
    #DATA[instance.Id.IntegerValue] = para
    DATA[instance.UniqueId] = data_entry_pack
    print(data_entry_pack)


def process_instance_applying(instance):
    print("###############")
    print(instance)
    print(instance.UniqueId)
    global DATA
    if instance.UniqueId not in DATA:
        type_name = instance.Symbol.LookupParameter("Type Name").AsString()
        family_name = instance.Symbol.FamilyName
        format_name = "{{{}}}:{}--->Cannot find matching ElementId---->{}".format(family_name, type_name, output.linkify(instance.Id, title = "Go to element"))
        print(format_name)
        return
    #para = DATA[instance.Id.IntegerValue]

    print(DATA[instance.UniqueId])
    data_entry_pack = DATA[instance.UniqueId]
    for data_entry in data_entry_pack:
        para_name, para_type, value = data_entry

        #definition = para.Definition
        #print definition.Name
        #print para.StorageType
        """
        if para.StorageType == DB.StorageType.Integer:
            #print para.AsInteger()
            value = para.AsInteger()
        if para.StorageType == DB.StorageType.Double:
            #print para.AsDouble()
            value = para.AsDouble()
        if para.StorageType == DB.StorageType.String:
            #print para.AsString()
            value = para.AsString()
        if para.StorageType == DB.StorageType.ElementId:
            #print para.AsElementId()
            value = para.AsElementId()
        """
        if para_name in ["Type Id", "Type"]:
            print("Skip assinging those parameter: {}".format(para_name))
            continue
        para = instance.LookupParameter(para_name)
        if para.IsReadOnly:
            print("<" + para_name + "> is read-only")
            continue

        if value is None:
            print("Skip assinging those parameter if has no value in record: {}".format(para_name))
        try:
            para.Set(value)
        except Exception as e:
            print("Cannot assign {} becasue: {}".format(para_name, e))




def get_families():
    panel_types = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsElementType().ToElements()
    OUT = []
    for panel_type in panel_types:
        family_name = panel_type.FamilyName
        type_name = panel_type.LookupParameter("Type Name").AsString()
        format_name = "{{{}}}:{}".format(family_name, type_name)
        OUT.append(format_name)

    if len(OUT) == 0:
        return None
    return sorted(OUT)

def get_all_instance_of_type(type_detail_name):
    panels = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).WhereElementIsNotElementType().ToElements()

    def match_name(panel):
        type_name = panel.Symbol.LookupParameter("Type Name").AsString()
        family_name = panel.Symbol.FamilyName
        #print panel
        #print type_name
        #print family_name
        format_name = "{{{}}}:{}".format(family_name, type_name)
        if format_name == type_detail_name:
            return True
        return False

    return filter(lambda x: match_name(x), panels)

def record_instance_property():

    # pick a famly to record instance
    type_detail_name = forms.SelectFromList.show(get_families(),
                                    multiselect = False,
                                    button_name='Select panel to record')

    print("Recording types: " + type_detail_name)
    # get all_instance of family
    all_instances = get_all_instance_of_type(type_detail_name)
    #print all_instances
    map(process_instance_recording, all_instances)
    #envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED")
    envvars.set_pyrevit_env_var("EA_INSTANCE_DATA_TRANSFER", DATA)

def map_instance_property():

    #  pick a family to load instance
    type_detail_name = forms.SelectFromList.show(get_families(),
                                    multiselect = False,
                                    button_name='Select panel to load data')

    print("Assiggning types: " + type_detail_name)
    # get all_instance of family
    all_instances = get_all_instance_of_type(type_detail_name)
    global DATA
    DATA = envvars.get_pyrevit_env_var("EA_INSTANCE_DATA_TRANSFER")
    #print all_instances
    t = DB.Transaction(doc, "Set instance from record")
    t.Start()
    map(process_instance_applying, all_instances)
    t.Commit()

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    DATA = dict()
    opt = ["Record panel instance info", "Assign panel instance info from record"]
    res = EA_UTILITY.dialogue(options = opt, main_text = "I want to ...")
    if res == opt[0]:
        record_instance_property()
    elif res == opt[1]:
        map_instance_property()
    else:
        pass
