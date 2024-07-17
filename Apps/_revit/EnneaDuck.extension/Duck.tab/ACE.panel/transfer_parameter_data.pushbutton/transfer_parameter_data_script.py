#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = """Transfer some data from one parameter to another. 
When you inherated from older file some parameter is carried over and now you have duplcated parameter container. 
Use this to cleanup the parameter panel"""
__title__ = "Transfer\nParameter Data"
__youtube__ = "https://youtu.be/onJCCtV0hts"
__tip__ = True

from pyrevit import forms #
from pyrevit import script #
import System


from EnneadTab import ERROR_HANDLE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


STORAGE_TYPE_MAP = {
    DB.StorageType.String: str,
    DB.StorageType.Integer: System.Int32,
    DB.StorageType.Double: System.Double,
    DB.StorageType.ElementId: DB.ElementId,
}

CATEGORY_OPTIONS = {"Sheet":DB.BuiltInCategory.OST_Sheets,
                    "View":DB.BuiltInCategory.OST_Views,
                    "Area":DB.BuiltInCategory.OST_Areas,
                    "Room":DB.BuiltInCategory.OST_Rooms}

@ERROR_HANDLE.try_catch_error()
def transfer_parameter_data():
    category = forms.SelectFromList.show(CATEGORY_OPTIONS.keys(),
                                         multiselect=False,
                                         title="Select Category",)
    if not category:
        return

    t = DB.Transaction(doc, __title__)
    t.Start()
    transfer_action(CATEGORY_OPTIONS.get(category))
    t.Commit()



def get_para(sample_element, button_name):
    try:
        selected_para = forms.select_parameters(sample_element,
                                            multiple=False,
                                                button_name=button_name)
    except:
        
        selected_para = forms.select_parameters(sample_element,
                                            multiple=False,
                                                button_name=button_name,
                                                include_type=False)

    return selected_para

def transfer_action(category):
    sample_element = DB.FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().FirstElement()
    if sample_element is None:
        NOTIFICATION.messenger("No element in the selected category")
        return

    source_para = get_para(sample_element, "Select <SOURCE> parameter to extract data")
            
    if source_para is None:
        return
    
    target_para = get_para(sample_element, "Select <TARGET> parameter to apply data")
    
    if target_para is None:
        return

    if source_para.definition.Name == target_para.definition.Name:
        NOTIFICATION.messenger("You are selecting same parameter. Cacnel")
        return

    if sample_element.LookupParameter(source_para.definition.Name).StorageType != sample_element.LookupParameter(target_para.definition.Name).StorageType:
        NOTIFICATION.messenger("You are selecting different storage type. The data cannot be transfered. Cacnel")
        return

    if sample_element.LookupParameter(target_para.definition.Name).IsReadOnly:
        NOTIFICATION.messenger("<{}> is a read only parameter or is being controled by template. The data cannot be transfered. Cacnel".format(target_para.definition.Name))
        return



    all_elements = DB.FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
    
    for element in all_elements:
        if not REVIT_SELECTION.is_changable(element):
            NOTIFICATION.messenger("Oops, some of the elements are owned by {} right now...".format(REVIT_SELECTION.get_owner(element)))
            
            continue
        local_para = element.LookupParameter(source_para.definition.Name)
        if local_para.StorageType == DB.StorageType.String:
            value = local_para.AsString()
            delete_data = "Transfered"
            
        elif local_para.StorageType == DB.StorageType.Integer:
            value = local_para.AsInteger()
            delete_data = -1
        elif local_para.StorageType == DB.StorageType.Double:
            value = local_para.AsDouble()
            delete_data = -1.0
        elif local_para.StorageType == DB.StorageType.ElementId:
            value = local_para.AsElementId()
            delete_data = DB.ElementId.InvalidElementId

        if value == delete_data:
            # this has been traansfered previoulsy
            continue

        target_type = STORAGE_TYPE_MAP.get(local_para.StorageType)


        if element.LookupParameter(target_para.definition.Name).IsReadOnly:
            print ("<{}> is a read only parameter or is being controled by template. The data cannot be transfered. Skip".format(target_para.definition.Name))
            continue
        
        try:
            element.LookupParameter(target_para.definition.Name).Set(value)
        except:
            try:
                element.LookupParameter(target_para.definition.Name).Set.Overloads[target_type](value)
            except:
                print ("Having trouble setting value...Cancel")
                continue


        if element.LookupParameter(source_para.definition.Name).IsReadOnly:
            print ("<{}> is a read only parameter or is being controled by template. The deleter data cannot be write.".format(source_para.definition.Name))
            continue
        element.LookupParameter(source_para.definition.Name).Set(delete_data)

    


################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    transfer_parameter_data()
    







