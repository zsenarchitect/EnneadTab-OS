
__title__ = "ExportCameraToRevit"
__doc__ = "You can recreate same 3D camera in Revit by exporting cameras from Rhino here first."

import Rhino # pyright: ignore
import scriptcontext as sc

from EnneadTab import FOLDER, NOTIFICATION
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def export_camera_to_revit():
    filepath = FOLDER.get_EA_dump_folder_file("EA_CAMERA_TRANSFER.3dm")

    file3dm = Rhino.FileIO.File3dm()
    file3md_options = Rhino.FileIO.File3dmWriteOptions()
    file3md_options.Version = 5

    #print doc.NamedViews
    #print doc.Views
    for view in sc.doc.NamedViews:
        print (view.Name)
        file3dm.AllNamedViews.Add(view)
    file3dm.Write(filepath, file3md_options)


    NOTIFICATION.messenger("Camera Data Ready to be imported at Revit side.")

if __name__ == "__main__":
    export_camera_to_revit()