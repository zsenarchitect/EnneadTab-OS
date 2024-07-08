

__title__ = "MaterialPrefix"
__doc__ = "Add prefix to material so when sessioning rhino the enscape can treat matreail seperately and not turn white."

import scriptcontext as sc

from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def material_prefix():
    mats = sc.doc.Materials
    mat_names = []
    doc_name = sc.doc.Name.split(".3dm")[0]
    print (doc_name)
    print (mats)
    print ("*******")
    for mat in mats:
        try:
            if mat.Name not in mat_names:
                if doc_name in mat.Name:
                    continue
                old_name =  mat.Name
                mat.Name = doc_name + "_" + old_name
                print ("{} --> {}".format(old_name, mat.Name))
                mat.CommitChanges()
                mat_names.append(mat.Name)
        except:
            continue


if __name__ == "__main__":
    material_prefix()