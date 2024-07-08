
__title__ = "ImportSelectedCamera"
__doc__ = "Import seleced camera from another file."


import scriptcontext as sc
import rhinoscriptsyntax as rs
import Rhino # pyright: ignore
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def import_selected_camera():
    filename = rs.OpenFileName(title = "pick a Rhino file to import view from",
                                filter = "Rhino 3D Models (*.3dm)|*.3dm||")
    if not filename:
        return

    f = Rhino.FileIO.File3dm.Read(filename)
    if (f.NamedViews.Count == 0):
        print ("no saved views in this file")
        return

    availible_view_names = [[x.Name, False] for x in f.NamedViews]
    try:
        availible_view_names.sort(key = lambda x: x[0].lower())
    except:
        pass
    availible_view_names.insert(0, ["<Check me to process all views, ignore selection below>", False])
    res = rs.CheckListBox(items = availible_view_names,
                            message = "select views to import from [{}]".format(filename),
                            title = "view importer")

    picked_view_name = []
    if not res:
        return
    
    for name, status in res:
        if "Check me" in name and status:
            picked_view_name = [x.Name for x in f.NamedViews]
            break
            
        if status:
            picked_view_name.append(name)


    rs.EnableRedraw(enable = False)
    for view_info in f.NamedViews:
        if view_info.Name in picked_view_name:
            sc.doc.NamedViews.Add(view_info)




if __name__ == "__main__":
    import_selected_camera()