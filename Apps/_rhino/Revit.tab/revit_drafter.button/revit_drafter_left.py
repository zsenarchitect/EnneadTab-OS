
__title__ = "RevitDrafterImport"
__doc__ = "Receive the drafting background from Revit and setup layer trees for supporting line style and filled region types."

import rhinoscriptsyntax as rs
import scriptcontext as sc

from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_CLEANUP, RHINO_LAYER
from EnneadTab import NOTIFICATION, FOLDER, DATA_FILE, ENVIRONMENT

import imp
ref_module = imp.load_source("random_layer_color_left", '{}\\Layer.tab\\random_layer_color.button\\random_layer_color_left.py'.format(ENVIRONMENT.RHINO_FOLDER))

def process_dwg(file, units):
    RHINO_CLEANUP.purge_block()
    rs.Command("_-import \"{}\" _ModelUnits={} -enter -enter".format(file, units))

    NOTIFICATION.messenger(main_text = "Come Back, come back!", sub_text = "Import Finish!")
    imported_objs = rs.LastCreatedObjects()
    #print imported_objs
    layers_used = set()
    new_block_name_used = set()

    if not imported_objs:
        NOTIFICATION.messenger(main_text = "Nothing imported!")
        
        return
    
    for obj in imported_objs:
        layer = rs.ObjectLayer(obj)
        layers_used.add(layer)
    layers_used = list(layers_used)


    for obj in imported_objs:
        if rs.IsBlockInstance(obj):
            new_block_name_used.add(rs.BlockInstanceName(obj))
    new_block_name_used = list(new_block_name_used)


    all_layers = rs.LayerNames()
    all_layers_user = [RHINO_LAYER.rhino_layer_to_user_layer(x) for x in all_layers]
    parent_layer_prefix = "EA_Drafting_Background_from_Revit"


    parent_layer_prefix = RHINO_LAYER.user_layer_to_rhino_layer(parent_layer_prefix)
    print (parent_layer_prefix)

    #only need to change layer
    change_objs_layer(imported_objs, parent_layer_prefix)
    safely_delete_used_layer(layers_used)
    #ref_module.random_layer_color(default_opt = True)
    RHINO_CLEANUP.purge_layer()
    return


def change_objs_layer(objs, parent_layer_prefix):
    for obj in objs:
        current_layer = rs.ObjectLayer(obj)
        desired_layer = parent_layer_prefix + "::" + current_layer
        rs.AddLayer(name = desired_layer)
        rs.ObjectLayer(obj, desired_layer)


def change_objs_layer_in_block(block_name, parent_layer_prefix):
    block_definition = sc.doc.InstanceDefinitions.Find(block_name)
    objs = block_definition.GetObjects()
    change_objs_layer(objs, parent_layer_prefix)


def safely_delete_used_layer(layers_to_remove):
    for layer in layers_to_remove:
        rs.DeleteLayer(layer)


def add_additional_layers(setting):
    line_style_names = setting["line_styles"]
    filled_region_type_names = setting["filled_region_type_names"]
    rs.EnableRedraw(False)
    for name in line_style_names:
        rs.AddLayer("OUT::Curves::{}".format(name))
    for name in filled_region_type_names:
        rs.AddLayer("OUT::FilledRegion::{}".format(name))

    ref_module.random_layer_color(default_opt = True)
    rs.CurrentLayer("OUT")




@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def revit_drafter():
    RHINO_CLEANUP.close_note_panel()



    # get_dwg path
    transfer_dwg = r"{}\{}".format(FOLDER.get_EA_local_dump_folder() , "EA_TRANSFER_DRAFT_BACKGROUND.dwg")

    # import and bundle layer
    file = FOLDER.get_EA_dump_folder_file("EA_TRANSFER_DRAFT_SETTING.sexyDuck")
    setting = DATA_FILE.read_json_as_dict(file)
    if not setting:
        NOTIFICATION.messenger(main_text = "No setting file found, please check your revit side.")
        return
    # unit_opts = ["Millimeters", "Feet", "Inches"]
    # units = rs.ListBox(unit_opts , message = "Use which unit for the DWG?" , default = unit_opts[0])
    # if units is None:
    #     return
    revit_unit = setting["revit_unit"]
    """possible revit unit
            feet, feet & inches
        inches, feet & inches
        feet
        inches
        millimeters"""
    if revit_unit == "millimeters":
        units = "Millimeters"
    elif revit_unit in ["feet, feet & inches", "feet"]:
        units = "Feet"
    elif revit_unit in ["inches, feet & inches", "inches"]:
        units = "Inches"
    else:
        NOTIFICATION.messenger(main_text = " bad unit, talk to SZ")
        return

    rs.EnableRedraw(False)
    process_dwg(transfer_dwg, units)


    # lock background layers


    # active view to top view, zoom extend
    rs.CurrentView(view = "Top")
    if not rs.IsViewMaximized("Top"):
        rs.MaximizeRestoreView( "Top" )

    dims = rs.ObjectsByType(geometry_type = 512, select = False, state = 0)#hide annotation
    rs.HideObjects(dims)
    rs.ZoomExtents()

    # create additional layer
    add_additional_layers(setting)


if __name__ == "__main__":
    revit_drafter()