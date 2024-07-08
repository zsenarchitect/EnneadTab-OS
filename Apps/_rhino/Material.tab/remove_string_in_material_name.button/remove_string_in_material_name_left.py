
__title__ = "RemoveStringInMaterialName"
__doc__ = "This button does RemoveStringInMaterialName when left click"

import scriptcontext as sc
import rhinoscriptsyntax as rs

def remove_string_in_material_name():
    doc_name = sc.doc.Name.split(".3dm")[0]

    search_text = rs.GetString("string to search to remove, type your string or enter to use current file name", defaultString = doc_name + "_")
 
    mats = sc.doc.Materials


    print(mats)
    print("*******")
    for mat in mats:
        try:
            if search_text in mat.Name:
                old_name = mat.Name
                mat.Name = mat.Name.split(search_text)[1]
                print("{} --> {}".format(old_name, mat.Name))
                mat.CommitChanges()

        except:
            continue