
__title__ = "RemoveStringInMaterialName"
__doc__ = "This button does RemoveStringInMaterialName when left click"

import scriptcontext as sc
import rhinoscriptsyntax as rs
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def remove_string_in_material_name():
    doc_name = sc.doc.Name.split(".3dm")[0]

    search_text = rs.StringBox("string to search to remove, type your string or enter to use current file name", 
                               default_value= doc_name + "_",
                               title = "I hate this name...")
 
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


if __name__ == "__main__":
    remove_string_in_material_name()