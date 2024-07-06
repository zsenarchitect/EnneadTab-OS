
__alias__ = "ArchiveFile"
__doc__ = "Archive files based on today's date, creation date or last modifyed date."


import os
import rhinoscriptsyntax as rs


from datetime import date, datetime
from Duckitect import FOLDER
from Duckitect.RHINO import RHINO_FORMS

def get_date(timestamp):
    return str(datetime.fromtimestamp(timestamp)).split(" ")[0]


def archive_file():

    file_paths = rs.OpenFileNames("pick file to archive",  filter = "Rhino Files (*.3dm)|*.3dm||")
    folder = rs.BrowseForFolder(message = "pick archive folder", title = "destination for archived file")
    for file_path in file_paths:
        print (file_path)

        file = FOLDER.get_file_name_from_path(file_path)

        ops = ["Today's date: {}".format(date.today()),
                "Last modify date: {}".format(get_date(os.path.getmtime( file_path))),
                "Created date: {}".format(get_date(os.path.getctime( file_path)))]
        sel = RHINO_FORMS.select_from_list(ops, message = "Pick date prefix for your file: [{}]".format(file), multi_select = False)
        date_prefix = sel.split(": ")[1]
        new_file = date_prefix + "_" + file
        #print new_file

        new_file_path = folder + "\\" + new_file
        print (new_file_path)
        FOLDER.copy_file(file_path, new_file_path)

    rs.MessageBox("All files have been archived.")

    ops = [FOLDER.get_file_name_from_path(x) for x in file_paths]
    ops.insert(0, "<Do not open any files.>")
    sel = RHINO_FORMS.select_from_list(ops, message = "Pick a file to open now", multi_select = False)
    if sel:
        sel = sel[0]
        if sel == "<Do not open any files.>":
            return
        print (file_paths)
        file = filter(lambda x: sel in x, list(file_paths))[0]
        print ("@@@@@" + file)
        rs.Command("!_-Open \"{}\"".format(file))

        rs.Command("!_Cancel all -Enter")
        rs.Redraw()
        #rs.MessageBox("Click on the 'Default White Arrow' or type 'Cancel' in command line to refresh new Rhino session.")
        """
        import Rhino # pyright: ignore
        Rhino.RhinoDoc.OpenFile(file)
        """
