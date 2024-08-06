#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = """All resource and documentation to help. 
+Turtorials
+Youtube playlist
+Family fomula cheatsheet
+Bugs reports
+Feedbacks
+EA websites
+Autodesk health websites
+Rhino and Revit cache folder
+Decoding the GUID name for BIM360 folder
+Installation for other enneadtab products
+Force kill sync monitor record.
+Training Videos: Scott's Friday training videos.
+Time sheet helper: Help you remember what you worked on each date."""
__context__ = 'zero-doc'
__title__ = "Assistant"
__tip__ = [__doc__,
           "You can use the timesheet feature to help you remember what project you worked on which date.\nThe record is only saved/viewable in your local computer",
           "All your BIM360 files have a local cache on your computer, which will take up precise C drive space.\nOvertime, the projects you are no longer editing will accumulate and new project might not be able to download cache with the remaining C drive space.\nThis is the number 1 leading cause for files cannot open in Revit.\nLuckily, you can open the cache folder directly with this helper button and you can safely delete anything that is no longer relavent.",
           "BIM360 default cache folder is named by GUID of the projects and files, which no one can read. However, you can use the little decoder from EnneadTab to retreive the name. Just copy-paste in the textbar and decode."]

from Autodesk.Revit import UI # pyright: ignore
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException



from pyrevit.revit import ErrorSwallower
from pyrevit import script, forms


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION, REVIT_SYNC
from EnneadTab import DOCUMENTATION, EXE, DATA_FILE, USER, IMAGE, ERROR_HANDLE, LOG, FOLDER, ENVIRONMENT


import traceback

import subprocess
import os
# uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
__persistentengine__ = True





# Create a subclass of IExternalEventHandler
class SimpleEventHandler(IExternalEventHandler):
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
                self.OUT = self.do_this(*self.kwargs)
            except:
                print ("failed")
                print (traceback.format_exc())
        except InvalidOperationException:
            # If you don't catch this exeption Revit may crash.
            print ("InvalidOperationException catched")

    def GetName(self):
        return "simple function executed by an IExternalEventHandler in a Form"



# A simple WPF form used to call the ExternalEvent
class AssistantUI(forms.WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        pass


    def __init__(self):

        self.pre_actions()
        xaml_file_name = 'external_links_UI.xaml'
        forms.WPFWindow.__init__(self, xaml_file_name)
        self.subtitle.Text = "Everything you need to know.."

        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.bt_jianbiaoku.Content = "Open 建标库 website"
        self.set_image_source(self.jianbiaoku_icon, "jianbiaoku_icon.png")
        self.set_image_source(self.youtube_icon, "youtube_icon.png")
        self.set_image_source(self.search_command_icon, "search_command_icon.png")
        self.set_image_source(self.family_fomula_icon, "family_fomula_icon.png")
        self.set_image_source(self.bug_icon, "bug_icon.png")
        self.set_image_source(self.autodesk_health_icon, "autodesk_health_icon.png")
        self.set_image_source(self.code_book_icon, "code_book_icon.png")
        self.set_image_source(self.cache_folder_icon, "cache_folder_icon.png")
        self.set_image_source(self.kill_monitor_icon, "dead_fish_icon.png")
        self.set_image_source(self.training_icon, "training_icon.png")
        self.set_image_source(self.documentation_icon, "documentation_icon.png")
        self.set_image_source(self.timesheet_icon, "timesheet_icon.png")
        self.set_image_source(self.meme_generator_icon, "meme_generator_icon.png")
        




        self.Show()


    @ERROR_HANDLE.try_catch_error()
    def ei_wiki_click(self, sender, args):
        script.open_url(r"https://ei.ennead.com/toolbox/BIMManual_01/0_Home%20Page.aspx")

    @ERROR_HANDLE.try_catch_error()
    def autodesk_health_click(self, sender, args):
        script.open_url("https://health.autodesk.com/")

    @ERROR_HANDLE.try_catch_error()
    def how_to_rhino_click(self, sender, args):
        script.open_url('https://github.com/zsenarchitect/EA_Dist/blob/main/Installation/How%20To%20Install.md')
    @ERROR_HANDLE.try_catch_error()
    def how_to_revit_click(self, sender, args):
        script.open_url('https://github.com/zsenarchitect/EA_Dist/blob/main/Installation/How%20To%20Install.md')
    @ERROR_HANDLE.try_catch_error()
    def how_to_cad_click(self, sender, args):
        path = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Library Docs\\CAD LISP\\CAD Command list.txt".format(ENVIRONMENT.L_DRIVE_HOST_FOLDER)

        subprocess.Popen(r'explorer /select, {}'.format(path))

    @ERROR_HANDLE.try_catch_error()
    def feedback_click(self, sender, args):
        opts = [["I have a EnneadTab related question", "Including trouble shooting/feature request/bug report"],
                ["I have a general question about Revit.", "Will be redirected to the General Applied Computing helpdesk."]]
        res = REVIT_FORMS.dialogue(main_text = "What is going on?", options = opts, title = "This plug-in sucks!")


        if res == opts[0][0]:
            REVIT_FORMS.notification(main_text = "You know what, directly message me thru Teams is the quickest way to get my attention.",
                                            sub_text = "My name is Sen Zhang, by the way.")
        else:
            script.open_url("https://airtable.com/shrWqu9wtGkdVwF53")

    @ERROR_HANDLE.try_catch_error()
    def youtube_click(self, sender, args):
        script.open_url("https://youtube.com/playlist?list=PLz3VQzyVrU1iyoGV-kzWhCPsmh9cQWWoV")
    @ERROR_HANDLE.try_catch_error()
    def learn_command_search_click(self, sender, args):
        script.open_url("https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=29754")
    @ERROR_HANDLE.try_catch_error()
    def family_fomula_click(self, sender, args):
        import family_fomula_cheat_sheet
        family_fomula_cheat_sheet.give_me_cheat_sheet()


    @ERROR_HANDLE.try_catch_error()
    def SD_reference_click(self, sender, args):
        path = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Library Docs\\SD Documentation Samples\\#PDF in this directory are reference only".format(ENVIRONMENT.L_DRIVE_HOST_FOLDER)

        subprocess.Popen(r'explorer /select, {}'.format(path))
    @ERROR_HANDLE.try_catch_error()
    def DD_reference_click(self, sender, args):
        path = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Library Docs\\DD Documentation Samples\\#PDF in this directory are reference only".format(ENVIRONMENT.L_DRIVE_HOST_FOLDER)

        subprocess.Popen(r'explorer /select, {}'.format(path))


    @ERROR_HANDLE.try_catch_error()
    def SH_code_click(self, sender, args):
        folder = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Library Docs\Codes".format(ENVIRONMENT.L_DRIVE_HOST_FOLDER)
        files = os.listdir(folder)
        special_folder = "#PDF in this directory are reference only"
        files.remove(special_folder)

        keyword = "<Open Entire Code Folder...>"
        files.insert(0, keyword)
        selected_opt = forms.SelectFromList.show(files, multiselect = False, title = "WHAT THE CODE IS GOING ON?????")
        if not selected_opt:
            return


        if keyword == selected_opt:

            path = "{}\\01_Revit\\04_Tools\\08_EA Extensions\\Library Docs\\DD Documentation Samples\\#PDF in this directory are reference only".format(ENVIRONMENT.L_DRIVE_HOST_FOLDER)
            subprocess.Popen(r'explorer /select, {}'.format(path))
            return

        filepath = folder + "\\" + selected_opt
        EXE.try_open_app(filepath)

    @ERROR_HANDLE.try_catch_error()
    def jianbiaoku_click(self, sender, args):
        script.open_url("http://www.jianbiaoku.com/")

        
    @ERROR_HANDLE.try_catch_error()
    def meme_generator_click(self, sender, args):
        script.open_url("https://imgflip.com/memegenerator")

        
    @ERROR_HANDLE.try_catch_error()
    def training_click(self, sender, args):
        folder_scott = "{}\\10_Learning Resources\\01_Revit\\Essentials".format(ENVIRONMENT.L_DRIVE_HOST_FOLDER)
        os.startfile(folder_scott)


    @ERROR_HANDLE.try_catch_error()
    def open_cache_revit_click(self, sender, args):
        path = r"{}\AppData\Local\Autodesk\Revit\PacCache".format(os.environ["USERPROFILE"])
        REVIT_FORMS.dialogue(main_text = "The cache in the upcoming folder 'C:\Users\YouName\AppData\Local\Autodesk\Revit' are all safe to delete. There are Crash journals, very old rvt links, unusaed locals, etc. from every version of Revit you have used.\n\n##BUT PLEASE DELETE THEM ONLY WHEN REVIT HAS BEEN CLOSED.##", sub_text = "You can delete those folders:\n  -Autodesk Revit 20xx\n  -PacCache\n\nNote:\nAfter Cache are deleted, you next Revit document openning will take longer than ususal because it will download cache again as needed.")

        subprocess.Popen(r'explorer /select, {}'.format(path))
    @ERROR_HANDLE.try_catch_error()
    def open_cache_rhino_click(self, sender, args):
        path = r"{}\AppData\Local\McNeel\Rhinoceros\temp".format(os.environ["USERPROFILE"])
        REVIT_FORMS.dialogue(main_text = "There are autosaves you might no longer need in the upcoming folder 'C:\Users\YouName\AppData\Local\McNeel\Rhinoceros' are safe to delete.\n\n##BUT PLEASE DELETE THEM ONLY WHEN RHINO HAS BEEN CLOSED.##", sub_text = "You can delete those folders:\n  -6.0\n  -7.0")

        subprocess.Popen(r'explorer /select, {}'.format(path))


    @ERROR_HANDLE.try_catch_error()
    def decode_guid_click(self, sender, args):
        # TO-DO: make also a selection list so user can decide which folder to delete cahe or restore recent crash local
        
        guid = self.textbox_cache_decoder.Text
        
        data = DATA_FILE.get_data("DOC_OPENER_DATA.sexyDuck", is_local=False)
        note = "This Guid has not been recored in EnneadTab DataBase."
        for doc_title, value in data.items():
            project_guid, file_guid,_ = value
            if guid == project_guid:
                note = "This Guid is a Project Guid. \nThis project contains:\n"
                for doc_title, value in data.items():
                    if value[0] == guid:
                        note += "[{}]\n".format(doc_title)
                break
            if guid == file_guid:
                note = "This Guid is a File Guid for [{}].".format(doc_title)
                break
        self.textbox_decoder.Text = note

    @ERROR_HANDLE.try_catch_error()
    def force_kill_sync_record_click(self, sender, args):
        REVIT_SYNC.kill_record()

    @ERROR_HANDLE.try_catch_error()
    def open_all_documentation_click(self, sender, args):
        DOCUMENTATION.print_documentation_book_for_review_revit()
        
        
    @ERROR_HANDLE.try_catch_error()
    def print_time_sheet_detail_click(self, sender, args):
        LOG.print_time_sheet_detail()  
        
    def handleclick(self, sender, args):
        print ("surface clicked")

    def close_click(self, sender, args):
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    AssistantUI()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()
    
