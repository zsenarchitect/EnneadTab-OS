
__title__ = "BindWorksession"
__doc__ = "Flatten the worksession to single file with named parent layer as file. Good for preparing files before sending out."


import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc
import os
import sys
import time

from EnneadTab import NOTIFICATION, SOUND, EMAIL
from EnneadTab.RHINO import RHINO_CLEANUP

def bind_worksession():
    begin_time = time.time()
    rs.EnableRedraw(False)
    
    final_path = rs.SaveFileName("Pick a final destination for the binded file.", filter = "Rhino File (*.3dm)|*.3dm||")
    if not final_path:
        return

    # sc.doc.SaveAs(final_path)
    # rs.Command("_SaveAs  '{}' -enter -enter".format(final_path))
    
    
    if not rs.DocumentPath():
        NOTIFICATION.messenger(main_text = "Saveas this file to the final location first!")
        return
    
    session_paths = list(sc.doc.Worksession.ModelPaths)
    my_path = "{}{}".format(rs.DocumentPath().replace("\\", "\\\\"), rs.DocumentName())
    print (my_path)
    print (session_paths)
    for path in session_paths:
        if path.endswith(rs.DocumentName()):
            session_paths.remove(path)
    print (session_paths)
    
    # move current file to layer structure
    my_name = rs.DocumentName()
    if my_name:
        my_name = my_name.replace(".3dm", "")
    else:
        my_name = "Untitled"
    change_objs_layer(rs.AllObjects(), decorate_parent_layer(my_name))
    
    try:
        if rs.IsLayer(decorate_parent_layer(my_name)):
            rs.CurrentLayer(decorate_parent_layer(my_name))
    except:
        pass
    
    
    
    map(process_session_path, session_paths)
    
    file_string_link = ""
    for file in session_paths:
        file_string_link += " Detach \"{}\"".format(file)
    rs.Command("-WorkSession   {}  Saveas \"{}\" Enter Enter".format(file_string_link, 
                                                                     EnneadTab.FOLDER.get_EA_dump_folder_file("temp_session.rws")))
    
    NOTIFICATION.messenger(main_text = "Purging Unused Layers, Materials and Blocks")
    RHINO_CLEANUP.purge_layer()
    RHINO_CLEANUP.purge_material()
    RHINO_CLEANUP.purge_block()
    collapse_all_layers()
    
    NOTIFICATION.messenger(main_text = "Begin saving binding file...this will take a while...")
    os.startfile(os. path. dirname(final_path))
    
    # rs.Command("_SaveAs  \"{}\" -enter ".format(final_path))
    sc.doc.SaveAs(final_path)
    SOUND.play_sound()
    NOTIFICATION.messenger(main_text = "Session Binding Done!")
    time_used = time.time() - begin_time
    EMAIL.email_to_self(subject="EnneadTab Auto Email: Session Binding Finished!",
                                body="After {}, Your binding file is saved, check below:".format(EnneadTab.TIME.get_readable_time(time_used)),
                                body_folder_link_list=[final_path],
                                body_image_link_list=["L:\\4b_Applied Computing\\03_Rhino\\12_EnneadTab for Rhino\\Source Codes\\Fun\\work_session_friend.jpg"])
    

    rs.DocumentModified(False)
    Rhino.RhinoApp.Exit(False)
    
def collapse_all_layers():
    layers = rs.LayerNames()
    for layer in layers:
        rs.ExpandLayer( layer, expand = False )

def process_session_path(path):
    NOTIFICATION.messenger(main_text = "Processing <{}>!\nThis might take a while depending on file size.".format(path))
    rs.Command("_-import \"{}\" -enter -enter".format(path))
    

    NOTIFICATION.messenger(main_text = "Come Back, come back!")
    imported_objs = rs.LastCreatedObjects()
    #print imported_objs
    layers_used = set()


    if not imported_objs:
        return

    for obj in imported_objs:
        layer = rs.ObjectLayer(obj)
        layers_used.add(layer)
    layers_used = list(layers_used)


    # for obj in imported_objs:
    #     if rs.IsBlockInstance(obj):
    #         new_block_name_used.add(rs.BlockInstanceName(obj))
    # new_block_name_used = list(new_block_name_used)



    parent_layer_prefix = os.path.basename(path).replace(".3dm", "")
    if parent_layer_prefix is None:
        parent_layer_prefix = path
    
 
    # parent_layer_prefix = RHINO_LAYER.user_layer_to_rhino_layer(parent_layer_prefix)
    print (parent_layer_prefix)

    #only need to change layer
    change_objs_layer(imported_objs, decorate_parent_layer(parent_layer_prefix))
    # safely_delete_used_layer(layers_used)

    
    return



def change_objs_layer(objs, parent_layer_prefix):
    rs.StatusBarProgressMeterShow(label = "Working on <{}>".format(parent_layer_prefix,  len(objs)), lower = 0, upper = len(objs), embed_label = True, show_percent = True)
    for i, obj in enumerate(objs):
        rs.StatusBarProgressMeterUpdate(position = i, absolute = True)
        
        current_layer = rs.ObjectLayer(obj)
        layer_color = rs.LayerColor(current_layer)
        layer_material = rs.LayerMaterialIndex(current_layer)
        desired_layer = parent_layer_prefix + "::" + current_layer
        try:
            rs.AddLayer(name = desired_layer)
            rs.LayerColor(desired_layer, layer_color)
            rs.LayerMaterialIndex(desired_layer, layer_material)
        except:
            pass
        rs.ObjectLayer(obj, desired_layer)
        
        
    rs.StatusBarProgressMeterHide()

def decorate_parent_layer(name):
    return "Binded Session [{}]".format(name)


