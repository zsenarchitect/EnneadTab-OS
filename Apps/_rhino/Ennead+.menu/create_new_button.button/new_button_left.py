
__title__ = "MakeANewButton"
import os
from ui import UI
"""
Use this button to create new button folder.
First allow to pick folder(from all folders that ends with .tab), use simple GUI
Then ask for name of the new button, and create that .button folder in the previous picked tab folder
then create a new .py file in the .button folder with the same name as the button.

This should be alloed to run indepdently
"""


def new_button():


    try:
        import rhinoscriptsyntax as rs
        os.startfile(__file__)
    except:
        tab_folders = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        UI(tab_folders)




#################################
if __name__ == "__main__":
    new_button()