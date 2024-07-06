
__alias__ = "CreateWorksession"
__doc__ = "Pick mutiple rhino files to create a session file instead of one after another. Good for dealing with heavy files."


import rhinoscriptsyntax as rs
from Duckitect import TIME

def create_worksession():

    files = rs.OpenFileNames(title = "Pick Rhino files to attach", filter = "Rhino File (*.3dm)|*.3dm||")
    #files = [r"I:\2135\0_3D\{}".format(file) for file in files]
    if not files:
        return
    #session_name = rs.StringBox(message = "What is the name of the Rhino session file?", default_value = None, title = "Duckitect Session Creation")
    session_file_path = rs.SaveFileName(title  = "What is the name of the Rhino session file?",
                                        filter = "Rhino Session File (*.rws)|*.rws||",
                                        folder = None,
                                        filename = "{}_XXX".format(TIME.get_YYYY_MM_DD()),
                                        extension = None)

    if not session_file_path:
        return

    file_string_link = ""
    for file in files:
        file_string_link += " Attach \"{}\"".format(file)
    rs.Command("-WorkSession  {} Saveas \"{}\" Enter".format(file_string_link, session_file_path))