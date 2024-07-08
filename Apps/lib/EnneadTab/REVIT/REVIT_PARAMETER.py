"""many helper func that help to dynamically add/pick project parameter, shared paramenter, """

import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)

import NOTIFICATION

try:

    from Autodesk.Revit import DB # pyright: ignore
    from Autodesk.Revit import UI # pyright: ignore
except:
    pass


def create_shared_parameter(doc,
                            para_name,
                            para_type,
                            para_group_name = None):
    """_summary_

    Args:
        doc (_type_): _description_
        para_name (_type_): _description_
        para_type (_type_): DB.SpecTypeId.Boolean.YesNo, etc
        para_group (_type_): _description_

    Returns:
        _type_: _description_
    """
    # make a dict about para_type lookup? or maybe REVIT_UNIT has something already?
    
    option = DB.ExternalDefinitionCreationOptions (para_name, para_type)
    if not para_group_name:
        
        definition_group = get_shared_para_group_by_name(doc,"EnneadTab",create_if_not_exist=True)
    else:
        definition_group = get_shared_para_group_by_name(doc,para_group_name,create_if_not_exist=True)
        
    definition = definition_group.Definitions.Create(option)
    
    return definition

    
def get_shared_para_group_by_name(doc, 
                                   para_group_name,
                                   create_if_not_exist=False):
    
    for definition_group in doc.Application.OpenSharedParameterFile().Groups:
        if definition_group.Name == para_group_name:
            return definition_group
    
    if create_if_not_exist:
        return doc.Application.OpenSharedParameterFile().Groups.Create(para_group_name)
    
    
    
    NOTIFICATION.messenger(main_text="Cannot find [{}] in shared parameter file.\nIs this loaded correctly?".format(para_group_name))
    return None

def get_shared_para_definition_by_name(doc, 
                                       para_name):
    

    shared_para_file = doc.Application.OpenSharedParameterFile()
    if not shared_para_file:
  
        NOTIFICATION.messenger(main_text='[{}]\nneed to have a valid shared parameter file'.format(doc.Title))
        filepath = "L:\\4b_Applied Computing\\01_Revit\\03_Library\\EA_SharedParam.txt"
        doc.Application.SharedParametersFilename = filepath
        
        shared_para_file = doc.Application.OpenSharedParameterFile()

    for definition_group in shared_para_file.Groups:
        for definition in definition_group.Definitions:
            if definition.Name == para_name:
                return definition



    NOTIFICATION.messenger(main_text="Cannot find [{}] in shared parameter file.\nIs this loaded correctly?".format(para_name))
    
    
    return None


def add_parameter_to_family_doc(family_doc, 
                                para_name, 
                                para_group,
                                default_value, 
                                is_instance_parameter = False):
    pass

def add_shared_parameter_to_project_doc(project_doc,
                                 para_definition,
                                 para_group,
                                 binding_cate_names,
                                 default_value,
                                 is_instance_parameter = False):
    """
    rework below to a dict, human category as key, OST_xxx as value
    cate_list = [("OST_Grids", "Grids"),
                ("OST_Levels", "Levels"),
                ("OST_Rooms", "Rooms"),
                ("OST_Areas", "Areas"),
                ("OST_Furniture", "Furniture")]

    cate_ids = [getattr(DB.BuiltInCategory , cate[0]) for cate in cate_list]
    cates = [DB.Category.GetCategory(doc, cate_id) for cate_id in cate_ids]
    
 
    """
    


    # define category set, should be  OST_Sheets
    cate_sets = DB.CategorySet()
    for cate in cates:
        
        cate_sets.Insert(cate)


    #instance binding
    binding = DB.InstanceBinding() if is_instance_parameter else DB.TypeBinding()
    binding.Categories = cate_sets

    #doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_GREEN_BUILDING)
    #doc.ParameterBindings.Insert(definition, binding, DB.BuiltInParameterGroup.PG_IFC)
    project_doc.ParameterBindings.Insert(para_definition, binding, DB.BuiltInParameterGroup.PG_DATA)
    # make a parser to parameter group
    
    
def get_parameter_by_name(fam_doc, 
                          para_name):
    
    for para in fam_doc.FamilyManager.Parameters:
        if para.Definition.Name == para_name:
            return para
    return None