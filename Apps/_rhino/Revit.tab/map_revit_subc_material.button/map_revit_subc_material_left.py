
__title__ = "MapRevitSubCategoryMaterial"
__doc__ = "Work with ExportSubCategoryMaterialTable on revit side. After you export the OST mapping there, this button help you create and map layer material based on layer name, if found in the OST mapping"
import rhinoscriptsyntax as rs
import scriptcontext as sc

from EnneadTab import NOTIFICATION, DATA_FILE, ENVIRONMENT
from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_MATERIAL

def get_layer_with_keyword(keyword):

    for layer in rs.LayerNames():
        if keyword in layer:
            return layer
    return None



@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def map_revit_subc_material():
    rs.EnableRedraw(False)
    data = DATA_FILE.read_json_as_dict_in_dump_folder("SUBC_MATERIAL_TABLE.json", use_encode= True)
    print(data)
    if not data:
        NOTIFICATION.messenger(main_text="There are no material data exported from Revit. \nUse the \"Export SubCategory Material Table\" button in \nEnneadTab for Revit to export the data first",
                                         image = ENVIRONMENT.get_EnneadTab_For_Rhino_root()+ "\\Source Codes\\Revit\\map_revit_subC_material_LG.png",
                                         animation_stay_duration = 7)
        return
    
    for subC_keyword, material_data in data.items():
        print (subC_keyword)
        # print material_data
        layer = get_layer_with_keyword(subC_keyword)
        if not layer:
            continue
        
        current_material_index = rs.LayerMaterialIndex(layer)
        current_material_name = rs.MaterialName(current_material_index)
        if current_material_name == material_data["shading"]["name"]:
            print ("Same name material already applied to this layer <{}>".format(layer))
            continue
        

        desired_material_index = sc.doc.Materials.Find(materialName = material_data["shading"]["name"],
                                                       ignoreDeletedMaterials = True)
        if desired_material_index != -1:
            print ("Desired material index: {}".format(desired_material_index))
            rs.LayerMaterialIndex(layer, desired_material_index)
            continue
        
        
        print ("########## Desired material not found in the document, will try to add it")
        
        RGBAR = (material_data["shading"]["color"]["red"],
                 material_data["shading"]["color"]["green"],
                 material_data["shading"]["color"]["blue"],
                 material_data["shading"]["transparency"],
                 material_data["shading"]["glossy"])
        desired_material_index, sample_sphere = RHINO_MATERIAL.create_material(name = material_data["shading"]["name"], 
                                                                                                RGBAR = RGBAR, 
                                                                                                return_index = True)
        # rs.DeleteObject(sample_sphere)
            
        
        
if __name__ == "__main__":
    map_revit_subc_material()