__doc__ = """Randomize the layer color, and rename the layer to to format below:
    Category_SubCategory
    
This tool does not change other existing setting for this export setting.
It makes life in Rhino easier after exporting contents over."""
__title__ = "DWG Export\nUpdate Layer"
__tip__ = True
from pyrevit import forms, script
from Autodesk.Revit import DB # pyright: ignore
import random

from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import NOTIFICATION, ERROR_HANDLE

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


def print_table(setting):
    t = DB.Transaction(doc, "Force regenerate")
    t.Start()
    doc.Regenerate()
    t.Commit()
    
    existing_option = setting.GetDWGExportOptions()
    exsiting_layertable = existing_option.GetExportLayerTable()
    for export_layer_key in exsiting_layertable.GetKeys():
        print  ("{}->{}".format(export_layer_key.CategoryName, \
                            export_layer_key.SubCategoryName))

def process_setting(sel_setting):
    old_name = sel_setting.Name
    t = DB.Transaction(doc, "make temp setting")
    t.Start()
    sel_setting.Name += "_temp"

    new_setting = DB.ExportDWGSettings.Create(doc, old_name, sel_setting.GetDWGExportOptions())
    t.Commit()



    #get the content in this setting
    existing_option = sel_setting.GetDWGExportOptions()##################diff from old
    exsiting_layertable = existing_option.GetExportLayerTable()

    new_export_layer_table = DB.ExportLayerTable()
    #safety = 0
    for export_layer_key in exsiting_layertable.GetKeys():
        #print export_layer_key.CategoryName
        #print export_layer_key.SubCategoryName
        new_layer_info = DB.ExportLayerInfo()
        """
        if export_layer_key.SubCategoryName == "Corner_Fin Main":
            print("x")
        if export_layer_key.SubCategoryName == "Clearance":
            print("y")
        """
        if export_layer_key.SubCategoryName == "":
            LayerName = "{}".format(export_layer_key.CategoryName)
        else:
            LayerName = "{}_{}".format(export_layer_key.CategoryName, \
                                        export_layer_key.SubCategoryName)
        if new_layer_info.LayerName != LayerName or new_layer_info.LayerName == "{{}}".format(export_layer_key.CategoryName):
            new_layer_info.LayerName = LayerName
            new_layer_info.CutLayerName = LayerName
            new_layer_info.ColorNumber = random.randint(1,255)

        #print new_layer_info.LayerName
        new_export_layer_table.Add(export_layer_key, new_layer_info)

        """
        if "bridge" in export_layer_key.SubCategoryName.lower():
            print("---")
            print(export_layer_key.SubCategoryName)
            print(LayerName)
        """
        #print "*"*8
        #safety += 1
        #if safety == 50000:
        #    break
    #print "$"*100

    t = DB.Transaction(doc, "Force regenerate before setting to new value")
    t.Start()
    doc.Regenerate()
    t.Commit()

    #ExportLayerTable = DB.ExportLayerTable()
    #new_dwg_export_option = DB.DWGExportOptions()
    #new_dwg_export_option.SetExportLayerTable(new_export_layer_table)
    existing_option.SetExportLayerTable(new_export_layer_table)
    #setting_name = "$$EnneadTab Rhino setting"

    
    
    t = DB.Transaction(doc,"new setting")
    t.Start()
    #DB.ExportDWGSettings.Create(revit.doc, setting_name, DWGExportOptions)
    sel_setting.SetDWGExportOptions(existing_option)
    NOTIFICATION.messenger(main_text = "<{}> layer names and colors updated.".format(new_setting.Name))
    #forms.alert("<{}> layer names and colors updated.".format(new_setting.Name))
    t.Commit()



    t = DB.Transaction(doc,"delete temp setting")
    t.Start()
    doc.Delete(new_setting.Id)
    t.Commit()

    t = DB.Transaction(doc,"restore good name")
    t.Start()
    sel_setting.Name = old_name
    t.Commit()

@ERROR_HANDLE.try_catch_error()
def main():

    existing_dwg_settings = DB.FilteredElementCollector(doc)\
                                .OfClass(DB.ExportDWGSettings)\
                                .WhereElementIsNotElementType()\
                                .ToElements()

    #get existing setting to start modify
    sel_settings = forms.SelectFromList.show(existing_dwg_settings, \
                                            name_attr = "Name", \
                                            multiselect = True,\
                                            button_name='Format Layer Names and Randomize Color', \
                                            title = "Select existing Export Setting to Modify.")
    if sel_settings == None:
        REVIT_FORMS.notification(main_text = "You didn't select any export setting.\nNothing is changed.",
                                                 self_destruct = 10)
        return
    
    
    
    TG = DB.TransactionGroup(doc, "update export layer")
    TG.Start()
    map(process_setting, sel_settings)
    TG.Assimilate()

###############################################

if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    main()




