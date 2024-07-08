
__title__ = "FindLayerInFiles"
__doc__ = "In a given folder, find which rhino file contains the keyword layer name. Good for traceback a illustrator file."


import Rhino # pyright: ignore
import rhinoscriptsyntax as rs

from EnneadTab import FOLDER, NOTIFICATION
from EnneadTab.RHINO import RHINO_FORMS, RHINO_LAYER



def find_layer_in_files():

    files = rs.OpenFileNames(title = "Select possible Rhino files",
                                        filter = "Rhino Files (*.3dm)|*.3dm||")
    if not files:
        return

    search_layer = rs.StringBox(message = "Key word in layer name to search, not case sensitive...",
                                default_value = "XXX", title = "wait...")
    if not search_layer:
        return

        
    logs = [process_file(x, search_layer) for x in files]
    OUT = ""
    for log in logs:
        if log == "":
            continue
        OUT += log
    RHINO_FORMS.notification(main_text = "Search keyword '{}' result see below:".format(search_layer),
                    sub_text = OUT,
                    height = 800,
                    width = 1000)


def process_file(file, search_layer):
    f = Rhino.FileIO.File3dm.Read(file)
    file_name = FOLDER.get_file_name_from_path(file)
    NOTIFICATION.toast(main_text = "Opening {}..".format(file_name))
    log = ""
    for layer in f.AllLayers:
        print (layer)
        if search_layer.lower() in str(layer).lower():
            message = "Find layer <{}> in file: {}".format(RHINO_LAYER.rhino_layer_to_user_layer(str(layer)), file_name)
            log += "\n{}".format(message)
            NOTIFICATION.toast(main_text = message)



    return log
 