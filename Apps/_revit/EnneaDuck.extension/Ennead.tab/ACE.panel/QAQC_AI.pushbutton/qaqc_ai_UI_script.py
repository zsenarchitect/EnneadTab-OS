#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Allow you to generate basic QAQC report based on current document, and use human language to chat with the report to get QAQC status.\nThis tool features openAI in the background for the chatbot part."
__title__ = "QAQC\nReporter"


import System

from pyrevit import script
from pyrevit import forms

import time


from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
# from pyrevit import forms #

# from pyrevit import revit #

import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_FORMS
from EnneadTab.FUN import JOKES
from EnneadTab import EXE, DATA_FILE, SOUND, TIME, ERROR_HANDLE, FOLDER, ENVIRONMENT
import traceback

from Autodesk.Revit import DB # pyright: ignore 
import random
# from Autodesk.Revit import UI # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
__persistentengine__ = True




def get_api_key():

    file_path = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc\EA_API_KEY.json"



    data = DATA_FILE.read_json_as_dict(file_path)
    return data["reporter_api_key"]






# Create a subclass of IExternalEventHandler
class conversation_SimpleEventHandler(IExternalEventHandler):
    """
    Simple IExternalEventHandler sample
    """

    # __init__ is used to make function from outside of the class to be executed by the handler. \
    # Instructions could be simply written under Execute method only
    def __init__(self, do_this):
        self.do_this = do_this
        self.kwargs = None
        self.OUT = None


    # Execute method run in Revit API environment.
    def Execute(self,  uiapp):

        try:

            try:
                #print "try to do event handler func"
                self.OUT = self.do_this(self.kwargs)
            except:
                self.OUT =  traceback.format_exc()
                print ("failed")
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"





# A simple WPF form used to call the ExternalEvent
class AI_Report_modelessForm(WPFWindow):
    """
    Simple modeless form sample
    """
    def initiate_form(self):
        sample = ["What are the critical issues?",
                    "Give a quick overall summery of the report",
                    "Who has the most critical warnings?"]
        self.tbox_input.Text = random.choice(sample)



    def pre_actions(self):

        return 
        self.clock_event_handler = conversation_SimpleEventHandler(clock_work)

        self.ext_event_clock = ExternalEvent.Create(self.clock_event_handler)
    
        return

    @ERROR_HANDLE.try_catch_error()
    def __init__(self):
        run_exe()
        self.pre_actions()
        xaml_file_name = "EA_QAQC_Reporter_ModelessForm.xaml" 
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab-GPT: Chat With Document (ft. openAI)"

        self.sub_text.Text = "Use openai's AI_Report to answer all kinds of questions in current document or from exisitng QAQC report."


        self.Title = "EnneadTab QAQC Reporter"
        #self.Width = 800
        self.Height = 1000
        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.set_image_source(self.pop_warning_img, "pop_warning.png")
    
        self.initiate_form()
        self.get_previous_conversation()
        self.session_name = "QAQC_SESSION_{}".format(TIME.get_formatted_current_time())
        self.Show()


    @property
    def log_file(self):
        file_name = "EA_QAQC_REPORT_LOG.json"
        return file_name

        return FOLDER.get_EA_dump_folder_file(file_name)

   
    def get_previous_conversation(self):
 
        if FOLDER.is_file_exist_in_dump_folder(self.log_file):
            record = DATA_FILE.get_data(self.log_file)
            self.tbox_conversation.Text = record["conversation_history"]
        else:
            self.tbox_conversation.Text = ""

    @ERROR_HANDLE.try_catch_error()
    def ask_Click(self, sender, e):
        # if not USER.IS_DEVELOPER:
        #     self.debug_textbox.Text = "WIP function."
        #     return
        query = self.tbox_input.Text
        data = dict()
        data["direction"] = "IN"
        if self.radio_bt_is_reading_pdf.IsChecked:
            data["method"] = "pdf"
            if not hasattr(self, "pdf"):
                self.debug_textbox.Text = "You need to pick pdf first...."
                
                return
            data["qaqc_file"] = self.pdf
        else:
            data["method"] = "text"
            if not hasattr(self, "report"):
                self.debug_textbox.Text = "You need to run the report first...."
                return
            data["qaqc_text"] = self.report
        data["query"] = self.tbox_input.Text
        data["api_key"] = get_api_key()
        data["store_name"] = self.session_name
        data["response"] = "No results."
        
        self.data_file = FOLDER.get_EA_dump_folder_file("QAQC_REPORT_DATA.json")
        DATA_FILE.set_data(data, self.data_file)
        
        run_exe()
        self.debug_textbox.Text = "Thinking..."
        
        
        max_wait = 60
        attempt = 0
        output = script.get_output()
        while attempt < max_wait:
            attempt += 1
            print(attempt)
            output.set_width(10)
            output.set_height(10)


            if attempt%3 == 0:
                self.debug_textbox.Text = JOKES.random_loading_message()
            
            time.sleep(1)
            temp_data = DATA_FILE.read_json_file_safely(self.data_file)
            if temp_data["direction"] == "OUT":
                 
                SOUND.play_sound("sound_effect_popup_msg3.wav")

                self.tbox_conversation.Text += "\n\nQ: {}\nA:{}".format(query, temp_data["response"])
                #self.tbox_conversation.Text = temp_data["response"]
                self.debug_textbox.Text = "Thinking finished."
                return


        self.debug_textbox.Text = "Thinking stopped."
        
  

            

    @ERROR_HANDLE.try_catch_error()
    def clear_history_Click(self, sender, e):
        if FOLDER.is_file_exist_in_dump_folder(self.log_file):
            FOLDER.remove_file_from_dump_folder(self.log_file)
        self.tbox_conversation.Text = ''
        #self.conversation_SimpleEventHandler.OUT = None
        pass

    def mouse_move_event(self, sender, args):
        #print "mouse down"
        #self.debug_textbox.Text = self.simple_event_handler.OUT
        pass

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()


    def close_Click(self, sender, args):
        self.save_conversation()
        #print "mouse down"
        self.Close()
        #self.debug_textbox.Text = self.simple_event_handler.OUT
        pass

    def save_conversation(self):
        record = dict()
        record["conversation_history"] = self.tbox_conversation.Text
        DATA_FILE.set_data(record, self.log_file)

    @ERROR_HANDLE.try_catch_error()
    def generate_report_click(self, sender, args):
        import QAQC_runner
        self.report = QAQC_runner.QAQC(script.get_output()).get_report(pdf_file = None, save_html = self.is_saving_html.IsChecked)

        if self.report == "PREVIOUSLY CLOSED":
            REVIT_FORMS.notification(main_text = "You have closed your last report window.", sub_text = "Please restart the QAQC reporter if you want to see the report again.")
            self.Close()

    @ERROR_HANDLE.try_catch_error()
    def bt_pick_pdf_clicked(self, sender, args):
        self.pdf = forms.pick_file(file_ext='*.pdf')
        if not self.pdf:
            return
        self.pdf_display.Text = self.pdf


    @ERROR_HANDLE.try_catch_error()
    def radial_bt_source_changed(self, sender, args):
        if self.radio_bt_is_reading_pdf.IsChecked:
            self.pdf_source_panel.Visibility = System.Windows.Visibility.Visible
        else:
            self.pdf_source_panel.Visibility = System.Windows.Visibility.Collapsed


def run_exe():

    exe_location = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Exe\QAQC_REPORT_READER\1.2\QAQC_REPORT_READER\QAQC_REPORT_READER.exe - Shortcut"


    
    EXE.open_file_in_default_application(exe_location)



def main():
    output = script.get_output()
    output.close_others()

    AI_Report_modelessForm()


if __name__ == "__main__":
    main()











  
        
