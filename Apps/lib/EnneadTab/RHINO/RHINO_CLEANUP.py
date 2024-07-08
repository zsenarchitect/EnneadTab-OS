
import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT
import ENVIRONMENT
if ENVIRONMENT.is_Rhino_environment():
    import Rhino # pyright: ignore
    import rhinoscriptsyntax as rs
  


def purge_layer():
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_Yes _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

def purge_material():
    rs.Command("_NoEcho _Purge _Pause _Materials=_Yes _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

def purge_block():
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_Yes _AnnotationStyles=_No _Groups=_No _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")

def purge_group():
    rs.Command("_NoEcho _Purge _Pause _Materials=_No _BlockDefinitions=_No _AnnotationStyles=_No _Groups=_Yes _HatchPatterns=_No _Layers=_No _Linetypes=_No _Textures=_No Environments=_No _Bitmaps=_No _Enter")


def save_small():
    rs.Command("savesmall")


def get_good_name(desired_name, name_pool):

    if name_pool is None:
        return desired_name
    i = 0
    while True:
        if desired_name not in name_pool:
            return desired_name
        surfix = "_index {}".format(i)
        desired_name = desired_name.replace(surfix, "")
        i += 1
        desired_name += "_index {}".format(i)
        
        
def close_note_panel():
    note_id = Rhino.UI.PanelIds.Notes
    Rhino.UI.Panels.ClosePanel(note_id)


def flatten_list(my_list):
    out = []
    for item in my_list:
        if isinstance(item, list):
            out.extend( flatten_list(item))
        else:
            out.append(item)
    return out


def reset_rhino(template, preserve_camera = True):
    # cam = rs.ViewCamera()
    cam, target = rs.ViewCameraTarget()
    lens = rs.ViewCameraLens()
    up = rs.ViewCameraUp()

    rs.DocumentModified(False)
    rs.Command('_NewDocument "{}"'.format(template))

    
    # rs.ViewCamera(None, cam)
    rs.ViewCameraTarget(None, cam , target)
    rs.ViewCameraLens(None, lens)
    rs.ViewCameraUp(None, up)