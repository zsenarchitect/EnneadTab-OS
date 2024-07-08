import os
import sys
root_folder = os.path.abspath((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root_folder)
import ENVIRONMENT
import ENVIRONMENT
if ENVIRONMENT.is_Rhino_environment():
    import Rhino # pyright: ignore
    import System # pyright: ignore

    import rhinoscriptsyntax as rs

    import Eto # pyright: ignore


    import scriptcontext as sc
    REF_CLASS = Eto.Forms.Dialog[bool]
else:
    REF_CLASS = object   

import sys
sys.path.append(r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib')

import os
import fnmatch

import itertools
flatten = itertools.chain.from_iterable
graft = itertools.combinations
try:
    import RHINO_UI
except:
    pass


# make modal dialog
class NotificationDialog(REF_CLASS):
    # Initializer
    def __init__(self, title, main_text,  sub_text,  self_destruct, button_name , width, height):
        # Eto initials
        self.Title = title
        self.Resizable = True
        self.Padding = Eto.Drawing.Padding(5)
        self.Spacing = Eto.Drawing.Size(5, 5)
        self.Icon = Eto.Drawing.Icon(r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\ennead-e-logo.png")
        #self.Bounds = Eto.Drawing.Rectangle()
        self.height = height
        self.width = width
        self.self_destruct = self_destruct
        self.main_text = main_text
        self.sub_text = sub_text
        self.Button_Name = button_name




        # initialize layout
        layout = Eto.Forms.DynamicLayout()
        layout.Padding = Eto.Drawing.Padding(5)
        layout.Spacing = Eto.Drawing.Size(5, 5)

        layout.AddSeparateRow(None, self.CreateLogoImage())

        # add message
        layout.BeginVertical()
        layout.AddRow(self.CreateMainTextBar())
        layout.EndVertical()

        layout.BeginVertical()
        layout.AddRow(self.CreateMessageBar())
        layout.EndVertical()



        # add buttons
        layout.BeginVertical()
        layout.AddSpace()
        layout.AddRow(*self.CreateButtons())
        layout.EndVertical()

        layout.Width = self.width
        layout.Height = self.height

        # set content
        self.Content = layout
        
        
        RHINO_UI.apply_dark_style(self)
        return
    
    
        if self.self_destruct:
            self.count_down(self.self_destruct)


    def count_down(self, life_span):
        import time
        for i in range(int(life_span)):
            time.sleep(i )
            print (int(life_span) - i)



    def CreateLogoImage(self):
        self.logo = Eto.Forms.ImageView()

        self.FOLDER_PRIMARY = r"L:\4b_Applied Computing\00_Asset Library"
        self.FOLDER_APP_IMAGES = r"{}\Database\app images".format(self.FOLDER_PRIMARY)
        self.LOGO_IMAGE = r"{}\Ennead_Architects_Logo.png".format(self.FOLDER_APP_IMAGES)
        temp_bitmap = Eto.Drawing.Bitmap(self.LOGO_IMAGE)
        self.logo.Image = temp_bitmap.WithSize(200,30)
        return self.logo

    def CreateMainTextBar(self):
        self.main_msg = Eto.Forms.Label()
        self.main_msg.Text = self.main_text
        self.main_msg.Font = Eto.Drawing.Font("Arial", 20)
        return self.main_msg

    # create message bar function
    def CreateMessageBar(self):
        self.msg = Eto.Forms.Label()
        self.msg.Text = self.sub_text
        self.msg.Font = Eto.Drawing.Font("Arial", 12)
        return self.msg
        #self.msg.HorizontalAlignment = Eto.Forms.HorizontalAlignment.Left




    def CreateButtons(self):
        """
        Creates buttons for either print the selection result
        or exiting the dialog
        """
        user_buttons = []

        self.btn_Run = Eto.Forms.Button()
        self.btn_Run.Text = self.Button_Name
        self.btn_Run.Click += self.btn_Run_Clicked
        user_buttons.append(self.btn_Run)

        self.btn_Cancel = Eto.Forms.Button()
        self.btn_Cancel.Text = "Cancel"
        self.btn_Cancel.Click += self.btn_Cancel_Clicked
        return user_buttons


        user_buttons.extend([ None, self.btn_Cancel])
        return user_buttons




    # function to run when call at button click
    def RunScript(self):
        # return selected items
        print ("Something important")




    # event handler handling clicking on the 'run' button
    def btn_Run_Clicked(self, sender, e):
        # close window after double click action. Otherwise, run with error
        self.Close(True)
        self.RunScript()


    # event handler handling clicking on the 'cancel' button
    def btn_Cancel_Clicked(self, sender, e):
        self.Close(False)



def show_NotificationDialog(title = "EnneadTab",
                            main_text = "",
                            sub_text = "",
                            self_destruct = None,
                            button_name = "Sure...",
                            width = 500,
                            height = 150):



    dlg = NotificationDialog(title, main_text, sub_text, self_destruct, button_name, width, height)
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dlg, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)

    if (rc):



        print ("User clicked primary button")
        return True

    else:
        print ("Dialog did not run")
        return None




def test():
    import traceback
    try:
        res = show_NotificationDialog(title = "new title",
                                        main_text = "Some main text " * 10,
                                        sub_text = "some sub text\n" * 5,
                                        self_destruct = 3,
                                        height = 500)
        print (res)
    except Exception as e:

        error =  traceback.format_exc()
        print (error)

        import NOTIFICATION
        NOTIFICATION.messenger(main_text = "error")
        filepath = r"C:\Users\szhang\Desktop\error.txt"
        import DATA_FILE
        DATA_FILE.save_list_to_txt([error], filepath, end_with_new_line = False)




#############################################################################################
if __name__ == "__main__":
    test()
