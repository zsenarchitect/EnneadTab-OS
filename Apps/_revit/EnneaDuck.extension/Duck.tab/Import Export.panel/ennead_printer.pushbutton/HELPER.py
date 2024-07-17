
from EnneadTab import ENVIRONMENT_CONSTANTS, NOTIFICATION
from Autodesk.Revit import DB # pyright: ignore



def find_definition_by_name(doc, name):
    for definition_group in doc.Application.OpenSharedParameterFile().Groups:
        for definition in definition_group.Definitions:
            if definition.Name == name:
                return definition
    return None

def create_color_setting_to_sheet(doc):
    sample_sheet = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().FirstElement()
    para = sample_sheet.LookupParameter("Print_In_Color")
    if para:
        NOTIFICATION.messenger(main_text='[Print_In_Color] parameter already exist in current file.')
        return
    

    shared_para_file = doc.Application.OpenSharedParameterFile()
    if not shared_para_file:
        NOTIFICATION.messenger(main_text='[{}]\nneed to have a valid shared parameter file'.format(doc.Title))
        filepath = "{}\\01_Revit\\03_Library\\EA_SharedParam.txt".format(ENVIRONMENT_CONSTANTS.HOSTER_FOLDER)
        doc.Application.SharedParametersFilename = filepath

    definition = find_definition_by_name(doc, "Print_In_Color")
    
            
    if definition is None:
        option = DB.ExternalDefinitionCreationOptions ("Print_In_Color", DB.SpecTypeId.Boolean.YesNo)
        definition_group = list(doc.Application.OpenSharedParameterFile().Groups)[0]
        definition = definition_group.Definitions.Create(option)
    
  
    
    t = DB.Transaction(doc, "add print_in_color parameter to sheet")
    t.Start()
   
    


    # define category set, should be  OST_Sheets
    cate_sets = DB.CategorySet()
    cate = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Sheets)
    cate_sets.Insert(cate)


    #instance binding
    binding = DB.InstanceBinding()
    binding.Categories = cate_sets

    doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_DATA)

    
    for sheet in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements():
        sheet.LookupParameter(definition.Name).Set(False)
    t.Commit()
    
    
    NOTIFICATION.messenger(main_text='[Print_In_Color] parameter added to the current document.')
    



def create_issue_para_to_sheet(doc, issue_name):
    
    sample_sheet = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().FirstElement()
    para = sample_sheet.LookupParameter(issue_name)
    if para:
        NOTIFICATION.messenger(main_text='[{}] parameter already exist in current file.'.format(issue_name))
        return
    

    shared_para_file = doc.Application.OpenSharedParameterFile()
    if not shared_para_file:
        NOTIFICATION.messenger(main_text='[{}]\nneed to have a valid shared parameter file'.format(doc.Title))
        filepath = r"L:\4b_Applied Computing\01_Revit\03_Library\EA_SharedParam.txt"
        doc.Application.SharedParametersFilename = filepath

    definition = find_definition_by_name(doc, issue_name)
    
            
    if definition is None:
        option = DB.ExternalDefinitionCreationOptions (issue_name, DB.SpecTypeId.String.Text)
        definition_group = list(doc.Application.OpenSharedParameterFile().Groups)[0]
        definition = definition_group.Definitions.Create(option)
    
  
    
    t = DB.Transaction(doc, "add [{}] parameter to sheet".format(issue_name))
    t.Start()
   
    


    # define category set, should be  OST_Sheets
    cate_sets = DB.CategorySet()
    cate = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_Sheets)
    cate_sets.Insert(cate)


    #instance binding
    binding = DB.InstanceBinding()
    binding.Categories = cate_sets

    doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_DATA)

    
    for sheet in DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements():
        sheet.LookupParameter(definition.Name).Set(False)
    t.Commit()
    
    
    NOTIFICATION.messenger(main_text='[{}] parameter added to the current document.'.format(issue_name))
    


if __name__ == "__main__":
    pass