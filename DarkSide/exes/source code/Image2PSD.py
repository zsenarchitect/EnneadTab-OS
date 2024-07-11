"""MAKE TO EXE AND RUN"""

import sys
sys.path.append("..\lib")
import EnneadTab

sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Dependency Modules\win32ctypes')
import win32api
import win32com.client
import os


def js_relink(app, new_img_path):
    jscode = r"""
    var desc = new ActionDescriptor();
    desc.putPath(stringIDToTypeID('null'), new File("{}"));
    executeAction(stringIDToTypeID('placedLayerRelinkToFile'), desc, DialogModes.NO);
    """.format(new_img_path)
    JavaScript(app, jscode)

def JavaScript(app, js_code):
    #app = ps.Application()
    app.doJavaScript(js_code)



@EnneadTab.ERROR_HANDLE.try_catch_error
def process_PSD():
    # opens ps
    global psApp
    psApp = win32com.client.Dispatch("Photoshop.Application")
    from os import environ as OS_ENV
    dump_folder = "{}\Documents\EnneadTab Settings\Local Copy Dump".format(OS_ENV["USERPROFILE"])
    data_file = r"{}\EA_PSD_STACK.txt".format(dump_folder)
    with open(data_file, "r") as f:
        lines = f.readlines()
    
    data = map(lambda x: x.replace("\n",""), lines)
    file_list, keep_doc_open, keep_ps_open = data[:-2], data[-2], data[-1]
    # global keep_doc_open
    # global keep_ps_open
    keep_doc_open = int(keep_doc_open[-1])
    keep_ps_open = int(keep_ps_open[-1])
    map(process_file, file_list)
    
    if not keep_ps_open:
        psApp.Quit()



def process_file(file_path):

    main_doc = psApp.Open(file_path)
    doc = psApp.Application.ActiveDocument
    layer = doc.ArtLayers[0]
    layer.name = get_file_name(file_path)
    
    surfixs = ["_depth","_materialId", "_objectId", "_alphaMask"]
    for surfix in surfixs:
        add_surfix_img_as_layer(doc, file_path, surfix)


    #js_relink(psApp, img1)
    
    PSD_path = file_path.replace(get_extension(file_path), ".psd")
    doc.SaveAs(PSD_path)
    if not keep_doc_open:
        doc.Close(2)# silent mode

def get_extension(file_path):
    if ".png" in file_path:
        return ".png"
    if ".jpg" in file_path:
        return ".jpg"

def get_file_name(file_path):
    return file_path.split("\\")[-1].split(".")[0]

def add_surfix_img_as_layer(current_doc, file_path, surfix):
    """
    if ".png" in file_path:
        file_name = file_path.split(".png")[0]
    if ".jpg" in file_path:
        file_name = file_path.split(".jpg")[0]
    new_img =  "{}{}{}".format(file_name, surfix, get_extension(file_path))
    """
    new_img =  file_path.replace(get_file_name(file_path), get_file_name(file_path) + surfix)

    from os.path import exists
    if not exists(new_img):
        return
    
    psApp.Load(new_img)
    psApp.ActiveDocument.Selection.SelectAll()
    psApp.ActiveDocument.Selection.Copy()
    psApp.ActiveDocument.Close()

    # new blank layer
    current_doc.ArtLayers.Add()

    # get layer to change
    layer = current_doc.ArtLayers[0]
    layer.name = get_file_name(file_path) + surfix
    psApp.ActiveDocument.Paste()
    #current_doc.Paste()

    





if __name__== "__main__":
    process_PSD()
