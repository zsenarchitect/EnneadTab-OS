
__title__ = "LoadEnscapeToPsd"
__doc__ = "This button does LoadEnscapeToPsd when left click"

import rhinoscriptsyntax as rs

from EnneadTab import FOLDER, EXE, DATA_FILE
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def load_enscape_to_psd():
   
    file_collection = list(rs.OpenFileNames())

    def identify_file(x):
        return x.replace("_materialId","").replace("_objectId", "").replace("_depth", "").replace("_alphaMask", "")

    file_collection = [identify_file(x) for x in file_collection]
    file_collection = list(set(file_collection))
    option_list = [["Keep Photoshop open", True],
                    ["Keep PSD open", True]]
    if not option_list:
        return
    res = rs.CheckListBox(items = option_list,
                            message= "Action after compiling",
                            title="EnneadTab Enscape stacking")
    if not res:
        return
    keep_ps_open, keep_doc_open = [x[-1] for x in res]
    OUT = file_collection
    OUT.append("#$#KEEP DOC OPEN = {}".format( int(keep_doc_open)))
    OUT.append("#$#KEEP PS OPEN = {}".format( int(keep_ps_open)))
    print(OUT)
    dump_file = "{}\EA_PSD_STACK.txt".format(FOLDER.get_EA_local_dump_folder())
    DATA_FILE.save_list_to_txt(OUT, dump_file)

    exe_path = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\Load_Enscape_Image_As_PSD_exe\Load_Enscape_Image_As_PSD_exe.exe"
    EXE.open_file_in_default_application(exe_path)
    """sample
    I:\2135\1_Study\EA 2022-09-12 mushroom stem cladding study\raw render\cam 04_opt UHPC.png
    I:\2135\1_Study\EA 2022-09-12 mushroom stem cladding study\raw render\cam 04_opt metal.png
    #$#KEEP DOC OPEN = 0
    #$#KEEP PS OPEN = 0
    """


if __name__ == "__main__":
    load_enscape_to_psd()