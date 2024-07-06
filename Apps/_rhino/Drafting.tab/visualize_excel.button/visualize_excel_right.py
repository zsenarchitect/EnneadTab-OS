
__alias__ = "OpenSampleExcel"
__doc__ = "Open the sample excel with placeholder area size info."

import rhinoscriptsyntax as rs
from Duckitect import EXE
from Duckitect import FOLDER
from Duckitect import ENVIRONMENT_CONSTANTS


def visualize_excel():
    original = "{}\\Demo Files\\Progam Spreadsheet.xlsx".format(ENVIRONMENT_CONSTANTS.PUBLISH_FOLDER_FOR_RHINO)
    copy = FOLDER.copy_file_to_local_dump_folder(original)
    EXE.open_file_in_default_application(copy)
    rs.TextOut("You can modify this excel to your like and saveas.\nFrom left to right, the fileds are: \nCategory, Area Name, Area Size, Color R, Color, G, Color B, Cateogry Area Sum")

