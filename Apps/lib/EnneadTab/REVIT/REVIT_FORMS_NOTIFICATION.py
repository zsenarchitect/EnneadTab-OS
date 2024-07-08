try:
    from pyrevit.forms import WPFWindow

    from pyrevit import script #


    from Autodesk.Revit import DB # pyright: ignore 
except:
    globals()["WPFWindow"] = object # this is to trick that class can be used
    
    
import os
import traceback
import time
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import ENVIRONMENT
"""
use this to do basic info dialogue, no func can run, no return of Information
"""


# A simple WPF form used to call the ExternalEvent
class ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def __init__(self,
                main_text,
                sub_text,
                button_name,
                window_title,
                self_destruct,
                window_width,
                window_height):


        xmal_template = "{}\REVIT\REVIT_FORMS_NOTIFICATION.xaml".format(ENVIRONMENT.get_EnneadTab_module_root())
        WPFWindow.__init__(self, xmal_template)
        self.title_text.Text = main_text
        self.simple_text.Text = sub_text
        self.primary_button.Content = button_name
        self.foot_text.Text = ""
        self.Title = window_title
        self.Height = window_height
        self.Width = window_width

        self.Show()


        if self_destruct > 0:
            self.timer(self_destruct)


    def primary_button_click(self, sender, e):
        self.close_action()


    def timer(self, life_span):
        #print "inside closer"

        deco_1 = "<"
        deco_2 = ">"
        segement = 5
        for i in range(life_span * segement,0,-1):

            if i % segement != 0:
                self.primary_button.Content = deco_1 + self.primary_button.Content + deco_2
                try:
                    print ("")
                except Exception as e:
                    pass
                    #print_note(e)
            else:
                self.primary_button.Content = self.primary_button.Content.replace(deco_1, "").replace(deco_2, "")
                try:
                    print( i / segement)
                except Exception as e:
                    pass
                    #print_note(e)
            self.foot_text.Text = "Window will close in {} seconds".format(i / segement)
            time.sleep(1.0/segement)
        self.close_action()

    def close_action(self):
        self.Close()
        #output = script.get_output()
        #output.close()
