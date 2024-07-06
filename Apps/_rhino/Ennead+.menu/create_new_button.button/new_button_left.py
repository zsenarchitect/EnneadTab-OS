
__alias__ = "Make A New Button"
from ui import UI
"""
Use this button to create new button folder.
First allow to pick folder(from all folders that ends with .tab), use simple GUI
Then ask for name of the new button, and create that .button folder in the previous picked tab folder
then create a new .py file in the .button folder with the same name as the button.

This should be alloed to run indepdently
"""


def new_button():
    tab_folders = r"C:\Users\szhang\github\Duckitect-for-Rhino\Toolbar"


    try:
        import rhinoscriptsyntax as rs
        print ("At the moment, plase make new button from the IDE. Later can make a compatible version that work with ironpython")
    except:
        UI(tab_folders)




#################################
if __name__ == "__main__":
    new_button()