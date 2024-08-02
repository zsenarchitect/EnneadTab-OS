#!/usr/bin/python
# -*- coding: utf-8 -*-

"""note to self:
this tool is getting heavy, should consider spliting to smaller files and restrucrure for Exporter 2.0"""


__doc__ = "A great helper for your print on deadline. Feastures include:\n  -pdf, dwg, jpg export together\n  -Package export files to subfolders in destination folder by assigned prefix and file type\n  -Prefix for auto numbering\n  -Email result as a link to folder.\n  -Time esitmation, with increasing accuracy the more you export\n  -Identify color setting per parameter on sheet. So you can mix color and BW export together.\n  -Option to sync and close files after exporting done.\n  -Export sheets by revision mark instead of printSet, and allow selective export without desrupting shared printSet.\n  -Export views on sheet seperatedly for dwg.\n  -Export from links or open docs.\n  -Merge pdf after export.\n  -JOKE while exporting."
__title__ = "Ennead\nExporter"
__tip__ = True
# from pyrevit import forms #
from pyrevit import script #
from pyrevit.revit import ErrorSwallower
# from pyrevit import revit #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION, REVIT_EVENT

from EnneadTab import JOKE, DATA_FILE, NOTIFICATION, ENVIRONMENT, SOUND, SPEAK, ERROR_HANDLE, FOLDER, IMAGE, USER, EMAIL, LOG
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore
import traceback

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

import clr # pyright: ignore
clr.AddReference('System.Windows.Forms')
# clr.AddReference('IronPython.Wpf')

# find the path of ui.xaml

from pyrevit import forms
from pyrevit.forms import WPFWindow
import os
import sys

import re
import time
from datetime import date
import math

# this is needed only becasue when parsing tips from python files, a relative import will fail to find moudle
script_folder = os.path.dirname(__file__)
import sys
sys.path.append(script_folder)
import HELPER
import EXPORT_ACTION


class DataGrid_Preview_Obj(object):
    @staticmethod # making this a independent function to the class, not to instance obj
    def legalize_filename( name):
        if r"/" in name:
            pass#print "Windows file name cannot contain '/' in its name, i will replace it with '-'"
        if "*" in name:
            NOTIFICATION.messenger (main_text="* is found in <{}>. Better remove this.".format(name))
        return name.replace("/", "-")#.replace("*","")


    def __init__(self, view_or_sheet, file_id, index, extension, time_estimate, is_in_height_light_zone = False, is_sheet_group_prefix = False):

        # used to show zone in datagrid when there is more than one doc to print
        self.is_in_height_light_zone = is_in_height_light_zone


        if view_or_sheet is None:# used when initiating empty grid
            self.format_name = "XXX"
            self.time_estimate = 0
            self.extension = ".X"
            return
        self.item = view_or_sheet
        self.file_id = file_id
        self.index = index
        #self.__raw_name = "To be filled at runn time"
        self.extension = extension
        self.time_estimate = time_estimate
        self.sheet_name = DataGrid_Preview_Obj.legalize_filename(view_or_sheet.Name)
        self.sheet_number = DataGrid_Preview_Obj.legalize_filename(view_or_sheet.SheetNumber)



        if file_id is None:# used when not using file id prefix
            self.format_name = "{} - {}{}".format(self.sheet_number,
                                                self.sheet_name,
                                                extension)
        else:
            self.format_name = "{}_{}_{} - {}{}".format(file_id,
                                                        index,
                                                        self.sheet_number,
                                                        self.sheet_name,
                                                        extension)


        if is_sheet_group_prefix:
            # have to assume non-EA file has no such parameters
            sheet_group = self.item.LookupParameter("Sheet_$Group").AsString() if self.item.LookupParameter("Sheet_$Group") else "Sheet $Group Missing"
            sheet_series = self.item.LookupParameter("Sheet_$Series").AsString() if self.item.LookupParameter("Sheet_$Series") else "Sheet $Series Missing"

            self.format_name = "[{}]-[{}]_{} - {}{}".format(sheet_group,
                                                            sheet_series,
                                                            self.sheet_number,
                                                                self.sheet_name, 
                                                                extension)


    @property
    def raw_name(self):
        return self.format_name.replace(self.extension, "")


    @property
    def time_estimate_format(self):


        if self.time_estimate == 0:
            return "N/A"
        if int(self.time_estimate) < 60:
            return "{:.2f} s".format(self.time_estimate * 1.0)

        return "{:.2f} mins".format(self.time_estimate / 60.0)
    """
    @raw_name.setter
    def raw_name(self, val):
        self.__raw_name == self.format_name.replace(self.extension, "")

    @raw_name.deleter
    def raw_name(self, val):
        del self.__raw_name
    """

    def __str__(self):
        return "Preview_Object: {}".format(self.format_name)



class EmailData(object):
    def __init__(self, receiver_list, subject, body, is_adding_final_folder_link, embeded_images_list = None, additional_attachments_list = None):

        self.receiver_list = receiver_list
        self.subject = subject
        self.body = body
        self.is_adding_final_folder_link = is_adding_final_folder_link
        self.embeded_images_list = embeded_images_list
        self.additional_attachments_list = additional_attachments_list
        self.log_file_path = None

    def update_info(self, EXPORTER_UI):

        self.receiver_list = EXPORTER_UI.email_receivers.Text
        self.subject = EXPORTER_UI.email_subject_line.Text
        self.body = EXPORTER_UI.email_body.Text
        self.is_adding_final_folder_link = EXPORTER_UI.checkbox_add_folder_link.IsChecked
        self.body_folder_link_list = [EXPORTER_UI.copy_folder_path]
        if hasattr(EXPORTER_UI, "log_file_path"):
            self.log_file_path = EXPORTER_UI.log_file_path

    def update_attachments(self):
        attachments_list = forms.pick_file(file_ext = '*', restore_dir = True, multi_file = True, title = "Pick attachments")
        if not attachments_list:
            return
        self.additional_attachments_list = attachments_list

    def update_embeded_image(self):
        images_list = forms.pick_file(file_ext = '*', restore_dir = True, multi_file = True, title = "Pick images to embed in Email.")
        if not images_list:
            return
        self.embeded_images_list = images_list

    def send(self):
        if self.additional_attachments_list:
            self.additional_attachments_list = filter(lambda item: not(item is None or "autosave log" in item.lower()), self.additional_attachments_list)

            self.additional_attachments_list.append(self.log_file_path)
        else:
            self.additional_attachments_list = [self.log_file_path]


        #print self.additional_attachments_list
        EMAIL.email(sender_email = None,
                        receiver_email_list = self.receiver_list,
                        subject = self.subject,
                        body = self.body,
                        body_folder_link_list = self.body_folder_link_list,
                        body_image_link_list = self.embeded_images_list,
                        attachment_list = self.additional_attachments_list,
                        schedule_time = None)


class DataGrid_Id_Map_Obj(object):
    def __init__(self, doc, map_id):
        self.doc = doc
        self.doc_name = EA_Printer_UI.central_doc_name(doc)
        self.map_id = map_id


class ExportRecordData(object):
    def __init__(self, stable_id, doc_name, extension, time_span):
        # stable_id can be view and viewsheet
        self.id = stable_id
        self.doc_name = doc_name
        self.extension = extension
        self.time_span = time_span

    def update_time_span(self, time_span):
        self.time_span = time_span

class EA_Printer_UI(WPFWindow):
    #@ERROR_HANDLE.try_catch_error()
    @ERROR_HANDLE.try_catch_error()
    def __init__(self):
        xamlfile = script.get_bundle_file('EA_Printer_Form.xaml')
        #print xamlfile
        WPFWindow.__init__(self, xamlfile)
        self.initiation_finished = False


        # important data setup
        self.setting_file = "exporter_setting.sexyDuck"
        self.output_folder = "{}\EnneadTab Exporter".format(ENVIRONMENT.DUMP_FOLDER)
        FOLDER.secure_folder(self.output_folder)


        self.export_queue = []
        self.selected_sheets = []

        self.load_setting()

        self.initiate_empty_data_grid_preview()
        #self.update_data_grid_map_id()
        self.bug_log = "Debug Output:"
        #self.update_debug("self.export_queue = ".format(self.export_queue))
        self.is_printing = False
        self.orginal_doc_name = self.central_doc_name(doc)

        # generic form setup
        self.folder_status_display.Content = ""
        notes_A = ["Export from linked Revit.",
                "Formated names.",
                "Multiple file extension.",
                "Export by issue.",
                "Change color setting per sheet.",
                "Isolated view export for dwg."]

        notes_B = ["Alert after finish.",
                "Upload to folder with subfolder.",
                "Sync and close after export.",
                "Ordering output.",
                "Record time estimate.",
                "Auto combine PDF."]
        self.feature_sum_note = ""
        for note in notes_A + notes_B:
            self.feature_sum_note += "\n -{}".format(note)




        self.progress_bar.Value = 0
        self.progress_bar_display.Text = "\n\n\n"
        self.note.Text = "Notes: Support for 2021 and before dropped."
        self.copy_folder_note_A.Text = "Folder you pick (example: I:/2135/2_Record/2022-09-30 50% DD)\n    -FileId\n       -PDFs\n         -A101_xx.pdf\n         -A102_xx.pdf\n       -DWGs\n         -A101_xx.dwg\n         -A102_xx.dwg"
        self.copy_folder_note_B.Text = "For example above, the final selection folder should say '2022-09-30 50% DD', not '2022-09-30 50% DD/FileId'"
        self.button_main.Content = "Setting Incomplete"
        logo_file = IMAGE.get_image_path_by_name("logo_vertical_light.png")
        self.set_image_source(self.logo_img, logo_file)
        self.set_image_source(self.update_icon, "update_icon.png")
        self.set_image_source(self.monitor_icon, "monitor_icon.png")





        self.initiate_para_list_source()
        self.initiate_dwg_setting_list_source()

        self.textbox_combined_pdf_name.Text = "{}_{}_Combined".format(date.today(), doc.Title)
        self.email_sender.Text = "{}@ennead.com".format(os.environ["USERPROFILE"].split("sers\\")[1])

        if not os.path.exists(self.setting_file):
            DATA_FILE.set_data(dict(), self.setting_file)






        output = script.get_output()
        output.close_others()
        self.initiation_finished = True
        self.check_all_setting_ready()
        self.update_UI_enable_status()

    def print_debug(self, string):


        #print self.bug_log
        self.debug_panel.Text = string


    def update_debug(self, line):
        self.bug_log += "\n{}".format(line)




# index_all_sheets(get_full_docs(), print_out = False)
    def print_all_sheet_index(self):
        print ("--------indexing all the sheets including file not printing now.--------")
        sorted_dict = sorted(self.index_dict.items(), key = lambda x: x[1])
        #print sorted_dict
        for key, value in sorted_dict:
            print ("[{}] ---> {}".format(key, value))
        print ("-------- end of index--------")


    def index_all_sheets(self, print_out = False):

        def lookup_value(sheet, para_name):
            para = sheet.LookupParameter(para_name)
            if para:
                if para_name == "Sheet_$Order":
                    return para.AsInteger()
                else:
                    return para.AsString()
            else:
                return None
            
        self.index_dict = dict()
        for doc in self.docs_to_process:
            doc_sheets =  self.get_sheets_from_doc(doc)
            if doc_sheets == []:
                NOTIFICATION.messenger("Cannot find any good sheets in {}.\nCheck your Issue parameter name used to find sheets.".format(doc.Title))
                continue

            if self.radio_button_sheetGroup_sheetSeries_sheetNum_sheetName.IsChecked:

                doc_sheets.sort(key = lambda x: (lookup_value(x,"Sheet_$Group"),
                                                    lookup_value(x,"Sheet_$Series"),
                                                    x.SheetNumber),
                                                    reverse = False)
            else:
                if doc_sheets[0].LookupParameter("Sheet_$Order"):
                    doc_sheets.sort(key = lambda x: (lookup_value(x,"Sheet_$Order"),
                                                x.SheetNumber), reverse = False)
                else:
                    doc_sheets.sort(key = lambda x: x.SheetNumber, reverse = False)


            for i, sheet in enumerate(doc_sheets):
                self.index_dict[sheet.UniqueId] = "{0:03}".format( i + 1)


        if print_out:
            self.print_all_sheet_index()





    def get_availiable_issue_paras(self):
        sample_sheet = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().FirstElement()
        if sample_sheet is None:
            out = ["No Issue Para Found."]
            return out
        out = []
        pattern = re.compile("Issue (.+)")
        pattern_additional = re.compile("Sheet_\$Issue(.+)")
        for para in sample_sheet.Parameters:
            """
            if "Issue" not in para.Definition.Name:
                continue
            """

            if  pattern.match(para.Definition.Name):
                out.append(para.Definition.Name)
                continue

            if  pattern_additional.match(para.Definition.Name):
                out.append(para.Definition.Name)
                continue

        out.sort()

        if len(out) == 0:
            out = ["No Issue Para Found."]
        return out




    def get_availiable_dwg_settings(self):
        existing_dwg_settings = DB.FilteredElementCollector(doc).OfClass(DB.ExportDWGSettings).WhereElementIsNotElementType().ToElements()

        return [x.Name for x in existing_dwg_settings]

    def get_sheets_from_doc(self, doc):
        if doc is None:
            return []
        sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).WhereElementIsNotElementType().ToElements()

        sheets = sorted(list(sheets), key = lambda x: x.SheetNumber)
        return filter(self.is_sheet_in_current_issue_para, sheets)



    def save_setting(self):

        current_setting_data = DATA_FILE.get_data(self.setting_file)



        out_data = dict()
        out_data["last_use_time"] = time.time()

        # get infor from doc name id pair to be used in step 1 grid table
        if current_setting_data.has_key("doc_names_id_pair"):
            temp = current_setting_data["doc_names_id_pair"]
        else:
            temp = dict()
        for item in self.data_grid_doc_id_map.ItemsSource:
            doc_name, id = item.doc_name, item.map_id
            temp[doc_name] = id
        out_data["doc_names_id_pair"] = temp


        # restore checkbox status for other
        out_data["is_export_dwg"] = self.checkbox_dwg.IsChecked
        out_data["is_export_pdf"] = self.checkbox_pdf.IsChecked
        out_data["is_export_jpg"] = self.checkbox_jpg.IsChecked
        out_data["is_name_format_with_plotId"] = self.radio_button_plotId_sheetNum_sheetName.IsChecked
        out_data["is_name_format_with_sheetGroup"] = self.radio_button_sheetGroup_sheetSeries_sheetNum_sheetName.IsChecked
        out_data["is_play_sound"] = self.checkbox_play_sound.IsChecked
        out_data["is_combine_pdf"] = self.checkbox_combine_pdf.IsChecked
        #out_data["dwg_setting_name"] = self.dwg_setting_name
        out_data["is_sync_and_close"] = self.checkbox_sync_and_close.IsChecked
        out_data["is_export_view_on_sheet"] = self.checkbox_dwg_view_export.IsChecked
        out_data["is_color_by_sheet"] = self.radio_button_color_by_sheet.IsChecked
        out_data["copy_folder_path"] = self.textbox_folder.Text
        out_data["is_copy_folder"] = self.checkbox_copy_folder.IsChecked
        out_data["is_send_email"] = self.checkbox_send_email.IsChecked


        out_data["issue_name"] = self.issue_name
        out_data["local_issue_para_name"] = self.textbox_local_isse_para_name.Text
        out_data["dwg_setting_name"] = self.dwg_setting_name


        self.email_data.update_info(self)
        out_data["email_data_receivers"] = self.email_data.receiver_list
        out_data["email_data_subject_line"] = self.email_data.subject
        out_data["email_data_body"] = self.email_data.body
        out_data["email_data_is_add_folder_link"] = self.email_data.is_adding_final_folder_link
        out_data["email_data_additional_attachments_list"] = self.email_data.additional_attachments_list
        out_data["email_data_embeded_images_list"] = self.email_data.embeded_images_list



        """export time estimate time should be record on L drive file. so other people can see.
        will not include in local setting.

        temp = dict()
        for i in range(10):
            temp[i] = ("Test_{}".format(i), "test doc", "pdf", 20-i)
        out_data["export_time_table"] = temp
        # dict of list [stable id of export obj, doc name,  extension, time]
        """






        DATA_FILE.set_data(out_data, self.setting_file)

    def initiate_default_email_data(self):
        self.email_data = EmailData(receiver_list = self.email_receivers.Text,
                                    subject = self.email_subject_line.Text,
                                    body = self.email_body.Text,
                                    is_adding_final_folder_link = self.checkbox_add_folder_link.IsChecked)

    @ERROR_HANDLE.try_catch_error()
    def load_setting(self):
        try:
            data = DATA_FILE.get_data(self.setting_file)
        except:
        
            data = dict()
            DATA_FILE.set_data(data, self.setting_file)



        # set some default value if there were no json file before
        if not data:
            self.docs_to_process = [doc]
            self.doc_names_id_pair = {self.central_doc_name(doc): "Ennead"}
            if doc.IsWorkshared :
                self.doc_model_path_pair = {self.central_doc_name(doc): get_doc_path(doc)}
            else:
                self.doc_model_path_pair = {self.central_doc_name(doc): None}
                NOTIFICATION.messenger(main_text = "This document is not workshared.")
            self.update_data_grid_map_id()
            self.is_export_dwg = self.checkbox_dwg.IsChecked
            self.is_export_pdf = self.checkbox_pdf.IsChecked
            self.is_export_jpg = self.checkbox_jpg.IsChecked
            self.is_name_format_with_plotId = self.radio_button_plotId_sheetNum_sheetName.IsChecked
            self.is_name_format_with_sheetGroup = self.radio_button_sheetGroup_sheetSeries_sheetNum_sheetName.IsChecked
            self.is_play_sound = self.checkbox_play_sound.IsChecked
            self.is_combine_pdf = self.checkbox_combine_pdf.IsChecked
            self.is_sync_and_close = self.checkbox_sync_and_close.IsChecked
            self.is_export_view_on_sheet = self.checkbox_dwg_view_export.IsChecked
            self.is_color_by_sheet = self.radio_button_color_by_sheet.IsChecked
            self.copy_folder_path = self.textbox_folder.Text
            self.is_copy_folder = self.checkbox_copy_folder.IsChecked

            self.initiate_para_list_source()
            self.initiate_dwg_setting_list_source()
            self.issue_name = self.issue_para_list.ItemsSource[self.issue_para_list.SelectedIndex]
            self.dwg_setting_name = self.dwg_setting_list.ItemsSource[self.dwg_setting_list.SelectedIndex]


            self.initiate_default_email_data()
            return False


        # retrive as much key as possible in class data
        for key, value in data.items():

            #print key
            #print value
            #getattr(self, key) ----> to read  data
            setattr(self, key, value)


        # restore previous form condition
        self.docs_to_process = [doc]
        if doc.IsWorkshared :
            self.doc_model_path_pair = {self.central_doc_name(doc): get_doc_path(doc)}
        else:
            self.doc_model_path_pair = {self.central_doc_name(doc): None}
            NOTIFICATION.messenger(main_text = "This document is not workshared.")
        self.update_data_grid_map_id()
        self.checkbox_dwg.IsChecked = self.is_export_dwg
        self.checkbox_pdf.IsChecked = self.is_export_pdf
        self.checkbox_jpg.IsChecked = self.is_export_jpg
        self.radio_button_plotId_sheetNum_sheetName.IsChecked = self.is_name_format_with_plotId
        self.radio_button_sheetNum_sheetName.IsChecked = not(self.is_name_format_with_plotId)
        try:
            self.is_name_format_with_sheetGroup
        except:
            self.is_name_format_with_sheetGroup = False
        self.radio_button_sheetGroup_sheetSeries_sheetNum_sheetName.IsChecked = self.is_name_format_with_sheetGroup
        self.checkbox_play_sound.IsChecked = self.is_play_sound
        self.checkbox_combine_pdf.IsChecked = self.is_combine_pdf
        self.checkbox_sync_and_close.IsChecked = self.is_sync_and_close
        self.checkbox_dwg_view_export.IsChecked = self.is_export_view_on_sheet
        self.radio_button_color_by_sheet.IsChecked = self.is_color_by_sheet
        self.radio_button_color_BW_globally.IsChecked =not( self.is_color_by_sheet)
        self.textbox_folder.Text = self.copy_folder_path
        self.checkbox_copy_folder.IsChecked = self.is_copy_folder

        try:
            self.email_data = EmailData(receiver_list = self.email_data_receivers,
                                        subject = self.email_data_subject_line,
                                        body = self.email_data_body,
                                        is_adding_final_folder_link = self.email_data_is_add_folder_link,
                                        embeded_images_list = self.email_data_embeded_images_list,
                                        additional_attachments_list = self.email_data_additional_attachments_list)

            self.email_receivers.Text = self.email_data_receivers
            self.email_subject_line.Text = self.email_data_subject_line
            self.email_body.Text = self.email_data_body
            self.checkbox_add_folder_link.IsChecked = self.email_data_is_add_folder_link
            self.checkbox_send_email.IsChecked = self.is_send_email

        except Exception as e:
            print (e.message)
            self.initiate_default_email_data()


        """be careful when  to recover from json record, becasue if user switch to new doc,
            there might be no matching name.
        """
        for i, para in enumerate(self.get_availiable_issue_paras()):
            if self.issue_name  == para:
                self.issue_para_list.SelectedIndex = i + 1# to skip the default text on index 0
                break
        else:
            self.issue_para_list.SelectedIndex = 0

        try:
            self.textbox_local_isse_para_name.Text = self.local_issue_para_name
            if self.local_issue_para_name == self.issue_name:
                self.issue_name = self.textbox_local_isse_para_name.Text
        except:
            print (traceback.format_exc())
            pass # this for newly added check

        for i, setting in enumerate(self.get_availiable_dwg_settings()):
            if self.dwg_setting_name == setting:
                self.dwg_setting_list.SelectedIndex = i + 1# to skip the default text on index 0
                break
        else:
            self.dwg_setting_list.SelectedIndex = 0




        #except Exception as e:
            #print "Trouble reading data file becasue: {}".format(e)

        return True

    def initiate_para_list_source(self):
        para_list = self.get_availiable_issue_paras()
        para_list.insert(0,"...Pick Issue Para...")
        para_list.append("...Use Local Para Below...")
        self.issue_para_list.ItemsSource = para_list

    def initiate_dwg_setting_list_source(self):
        para_list = self.get_availiable_dwg_settings()
        para_list.insert(0,"...Pick DWG setting...")
        self.dwg_setting_list.ItemsSource = para_list

    @staticmethod
    def central_doc_name(doc):
        return doc.Title.replace("_{}".format(USER.USER_NAME),  "")

    def get_id_by_doc(self, doc):
        true_doc_name = self.central_doc_name(doc)
        if not self.doc_names_id_pair.has_key(true_doc_name):
            self.doc_names_id_pair[true_doc_name] = "0"

        return self.doc_names_id_pair[true_doc_name]

    @property
    def issue_symbol(self):
        return u"\u25A0"

    def is_sheet_in_current_issue_para(self, sheet):

        if "internal" in self.issue_name.lower() and not sheet.LookupParameter(self.issue_name)  and sheet.LookupParameter(self.issue_name).AsString() == self.issue_symbol:
            return True


        if not sheet.LookupParameter("Appears In Sheet List").AsInteger():
            return False


        if not sheet.LookupParameter(self.issue_name):
            return False


        if sheet.LookupParameter(self.issue_name).AsString() is None:
            return False

        #print sheet.LookupParameter(self.issue_name).AsString()
        if len(sheet.LookupParameter(self.issue_name).AsString()) != 0:
            return True

        #### below not important anymore ########

        if sheet.LookupParameter(self.issue_name).AsString() !=  self.issue_symbol:
            return False

        return True


    def update_data_grid_map_id(self):
        self.docs_to_process.sort(key = lambda x:x.Title)
        self.data_grid_doc_id_map.ItemsSource = [DataGrid_Id_Map_Obj(doc, self.get_id_by_doc(doc)) for  doc in self.docs_to_process]

    def initiate_empty_data_grid_preview(self):
        self.data_grid_preview.ItemsSource = []
        time_estimate = 0
        index = 999
        file_id = "-999"
        view_or_sheet = None
        extension = None
        is_in_height_light_zone = False
        for x in range(30):
            self.data_grid_preview.ItemsSource.append(DataGrid_Preview_Obj(view_or_sheet, file_id, index, extension, time_estimate, is_in_height_light_zone))
        self.data_grid_preview_title.Text = "Pending valid setting..."



    def update_data_grid_preview(self):
        #print "!!!!about to update preview grid"
        self.export_queue = []# to hold all the sheet objs.
        self.record = dict()# hold time data
        for id_map_obj in self.data_grid_doc_id_map.ItemsSource:
            doc = id_map_obj.doc
            sheets = self.get_sheets_from_doc(doc)
            self.export_queue.extend(sheets)

            for key, value in self.get_time_estimate_from_record(doc).items():
                self.record[key] = value

        if len(self.selected_sheets) != 0:
            sheet_ids = [x.UniqueId for x in self.selected_sheets]
            self.export_queue = filter(lambda x: x.UniqueId in sheet_ids, self.export_queue)

        #print "before updating preview grid, the export queue is \n{}".format(self.export_queue)
        #self.update_debug("before updating preview grid, the export queue is {}".format(self.export_queue))
        self.data_grid_preview.ItemsSource = []
        self.index_all_sheets()
        is_in_height_light_zone = False
        self.export_queue.sort(key = lambda x: "{}_{}".format(self.get_id_by_doc(x.Document), self.index_dict[x.UniqueId]))

        def get_time_estimate_by_sheet_and_extension(sheet, extension):
            key = "{}#{}".format(sheet.UniqueId, extension)
            if key in self.record.keys():
                return self.record[key]
            return 0

        estimated_total = 0
        for sheet in self.export_queue:


            index = self.index_dict[sheet.UniqueId]
            if self.is_name_format_with_plotId:
                file_id = self.get_id_by_doc(sheet.Document)
            else:
                file_id = None

            if self.is_export_pdf:
                extension = ".pdf"
                time_estimate = get_time_estimate_by_sheet_and_extension(sheet, extension)
                estimated_total += time_estimate
                preview_obj = DataGrid_Preview_Obj(sheet, file_id, index, extension, time_estimate, is_in_height_light_zone, is_sheet_group_prefix=self.is_name_format_with_sheetGroup)
                self.data_grid_preview.ItemsSource.append(preview_obj)

            if self.is_export_dwg:
                extension = ".dwg"
                time_estimate = get_time_estimate_by_sheet_and_extension(sheet, extension)
                estimated_total += time_estimate
                preview_obj = DataGrid_Preview_Obj(sheet, file_id, index, extension, time_estimate, is_in_height_light_zone, is_sheet_group_prefix=self.is_name_format_with_sheetGroup)
                self.data_grid_preview.ItemsSource.append(preview_obj)

            if self.is_export_jpg:
                extension = ".jpg"
                time_estimate = get_time_estimate_by_sheet_and_extension(sheet, extension)
                estimated_total += time_estimate
                preview_obj = DataGrid_Preview_Obj(sheet, file_id, index, extension, time_estimate, is_in_height_light_zone, is_sheet_group_prefix=self.is_name_format_with_sheetGroup)
                self.data_grid_preview.ItemsSource.append(preview_obj)

            # to flip height light color for next zone
            is_in_height_light_zone = not(is_in_height_light_zone)



        #self.data_grid_preview.ItemsSource.sort(key = lambda x: x.format_name)

        estimated_total = "{:.2f} mins".format(estimated_total / 60.0)
        self.data_grid_preview_title.Text = "{} items queued.\nEstimated total time = {}+. Total time excluding N/A item. ".format(len(self.data_grid_preview.ItemsSource), estimated_total)

        if len(self.data_grid_preview.ItemsSource) == 0:
            self.initiate_empty_data_grid_preview()
            self.button_main.IsEnabled = False
            self.button_main.Content = "Nothing to export.."




    def check_all_setting_ready(self):
        #self.print_debug()
        if not self.initiation_finished:
            return False

        self.button_main.BorderBrush = self.sample_color_disabled.Foreground


        if self.is_export_dwg + self.is_export_jpg + self.is_export_pdf == 0:
            self.button_main.Content = "Need at least one extension."
            self.initiate_empty_data_grid_preview()
            return False


        if self.is_copy_folder and self.copy_folder_path == "Folder Path...":
            self.button_main.Content = "Copy folder path missing."
            return False


        if self.issue_name == self.issue_para_list.ItemsSource[0]:
            self.button_main.Content = "Issue parameter not picked."
            self.initiate_empty_data_grid_preview() #this will affect what should display, so should update
            return False


        if self.issue_name == self.issue_para_list.ItemsSource[-1]:
            self.issue_name = self.textbox_local_isse_para_name.Text
            if len(self.issue_name) == 0:
                self.button_main.Content = "Locally defined issue Parameter cannot be empty."
                return False


        if self.is_export_dwg and self.dwg_setting_name == self.dwg_setting_list.ItemsSource[0]:
            self.button_main.Content = "DWG setting not picked."
            return False

        # check setting A, return False if not pass


        # cehck setting B, return False if not pass
        
        for item in self.data_grid_preview.ItemsSource:
            if "*" in item.format_name:
                NOTIFICATION.messenger(main_text="Please remove * at " + item.format_name)
                self.button_main.Content = "There are * in some name."
                return False




        # after passing all test, the script is readt to action export
        self.button_main.IsEnabled = True
        self.button_main.Content = "Ready to export!"
        self.button_main.BorderBrush = self.sample_color_green.Foreground

        self.update_data_grid_map_id() #this step is needed during iniitalization process
        self.update_data_grid_preview()
        return True
            #self.button_rename.Foreground = "#FF464646"






    def active_original_doc(self, doc_name):
        print ("!!!!!!!Activate {} ".format(doc_name))
        model_path = self.doc_model_path_pair[doc_name]


        """
        if model_path.CloudPath:
            #cloud_path = DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(System.Guid(data[1]), System.Guid(data[2]) )
            open_options = DB.OpenOptions()
            #ERROR_HANDLE.print_note( "setting active doc as {}".format(data[0]))
            return UI.UIApplication(app).OpenAndActivateDocument (model_path,
                                                                open_options,
                                                                False)
        """

        # this model path  is server path
        open_options = DB.OpenOptions()
        #ERROR_HANDLE.print_note( "setting active doc as {}".format(data[0]))
        try:
            return UI.UIApplication(REVIT_APPLICATION.get_app()).OpenAndActivateDocument (model_path,
                                                                                            open_options,
                                                                                            False)
        except Exception as e:
            print (traceback.format_exc())
            return None

    def open_doc_in_background(self, doc_name):
        #print "!!!Opening {} in background".format(doc_name)
        model_path = self.doc_model_path_pair[doc_name]
        open_options = DB.OpenOptions()
        if isinstance(model_path, DB.ModelPath):
            new_doc = REVIT_APPLICATION.get_app().OpenDocumentFile(model_path,
                                                                    open_options)
        elif isinstance(model_path, str):
            new_doc = REVIT_APPLICATION.get_app().OpenDocumentFile(model_path)

        #output.print_md( "background open file {}".format(doc_name))


    @ERROR_HANDLE.try_catch_error()
    def main_export_Clicked(self, sender, args):###sender and args must be here even when not used to pass data between GUI and python

        if "export finish" in self.button_main.Content.lower():
            self.Close()
            return

        if not self.check_all_setting_ready():
            return

        # ---- pre action ----
        self.save_setting()
        self.monitor_group.Visibility, self.data_grid_preview.Visibility = self.data_grid_preview.Visibility,self.monitor_group.Visibility




        self.doc_names_already_open = [self.central_doc_name(x) for x in REVIT_APPLICATION.get_top_revit_docs()]
        self.docs_to_be_opened_by_API = [x for x in self.docs_to_process if self.central_doc_name(x) not in self.doc_names_already_open]

        #depress open hook
        REVIT_EVENT.set_open_hook_depressed(stage = True)
        # EA_UTILITY.set_doc_change_hook_depressed(stage = True)
        # ERROR_HANDLE.print_note("my doc change hook depress satus = {}".format(EA_UTILITY.is_doc_change_hook_depressed()))

        time_start = time.time()
        #open background doc that neeed to be opeend
        with ErrorSwallower() as swallower:
            for doc in self.docs_to_be_opened_by_API:
                #print doc.Title
                self.open_doc_in_background(doc.Title)
        #timer how long background files used to open
        time_end = time.time()

        if len(self.docs_to_be_opened_by_API) > 0:
            EXPORT_ACTION.print_time("background loading {} files".format(self.docs_to_be_opened_by_API), time_end, time_start, use_minutes = False)

            ###!!!! no need to reactive primary doc if we are using post file name correction method
            #primary_doc = active_original_doc(orginal_doc_name).Document##function return UI doc ##try this to fix main doc pdf not print issue



        #open hook depression re-enable
        REVIT_APPLICATION.set_open_hook_depressed(stage = False)









        # ---- ACTION BEGIN ----

        self.Topmost = True
        self.is_printing = True
        self.is_printing_interupted = False
        self.button_cancel_export.Visibility = self.button_main.Visibility
        self.button_main.Content = "Exporting..."
        self.files_exported_for_this_issue = []


        #this is done here primaryly for the dwg bundles. The inner views need to know the file id as it comes out.
        self.file_id_dict = dict()
        for item in self.data_grid_preview.ItemsSource:
            self.file_id_dict[item.format_name] = item.file_id

        self.progress_bar.Value = 0
        self.progress_bar.Maximum = len(self.data_grid_preview.ItemsSource)
        #self.progress_bar.Visible  = True


        job_time_start = time.time()
        print("Let The Printing Begin:")
        self.Topmost = False
        current_sheet_id = None
        for i, preview_obj in enumerate(self.data_grid_preview.ItemsSource):
            if not self.is_printing:
                break
            #print "simulate print-->" + str(preview_obj)

            print ("\n\n-------{}/{} preparing : {} ---------".format(i + 1, len(self.data_grid_preview.ItemsSource), preview_obj))
            if len(self.data_grid_preview.ItemsSource) - i < 5:
                SPEAK.speak(None)

            time_start = time.time()
            # main export action
            #self.export(item)
            #print dir(preview_obj)
            view_or_sheet = preview_obj.item
            extension = preview_obj.extension
            file_name = preview_obj.format_name
            raw_name = preview_obj.raw_name

            # only update preview image for new sheet
            if current_sheet_id != view_or_sheet.UniqueId:
                self.update_preview_image(view_or_sheet)
                current_sheet_id = view_or_sheet.UniqueId

            #update laoding status for every export item
            self.update_loading_message(preview_obj)



            #file_name here contain extension
            if os.path.exists(os.path.join(self.output_folder, file_name)):
                os.remove(os.path.join(self.output_folder, file_name))


            if extension == ".pdf":
                is_color_by_sheet = self.is_color_by_sheet
                final_file = EXPORT_ACTION.export_pdf(view_or_sheet, raw_name, self.output_folder, is_color_by_sheet)
                self.files_exported_for_this_issue.append(final_file)

            if extension == ".dwg":
                is_export_view_on_sheet = self.is_export_view_on_sheet
                dwg_setting_name = self.dwg_setting_name
                DWG_option = DB.DWGExportOptions().GetPredefinedOptions(view_or_sheet.Document, dwg_setting_name)
                if DWG_option:
                    final_files = EXPORT_ACTION.export_dwg(view_or_sheet, raw_name, self.output_folder, dwg_setting_name, is_export_view_on_sheet)

                    self.files_exported_for_this_issue.extend(final_files)
                    for new_files in final_files:
                        self.file_id_dict[new_files] = self.file_id_dict[preview_obj.format_name]
                else:
                    print ("###############Cannot find this setting in the doc...cancel exporting...")
                    final_files = []
                    #is_success = False

            if extension == ".jpg":
                final_file = EXPORT_ACTION.export_image(view_or_sheet, raw_name, self.output_folder,  is_color_by_sheet = self.is_color_by_sheet)
                self.files_exported_for_this_issue.append(final_file)

            time_end = time.time()
            format_time = EXPORT_ACTION.print_time("sheet to {}".format(extension), time_end, time_start)
            preview_obj.time_estimate = time_end - time_start

            """
            EA_UTILITY.show_toast(app_name = "Ennead Exporter",
                                    title = "[{}] saved. {}".format(file_name, format_time),
                                    image = script.get_bundle_file("icon.png"),
                                    message = "{} more to do in current queue.".format(int(self.progress_bar.Maximum - i - 1)))
            """



            """copy new created file to final folder now"""
            remaining_objs = self.data_grid_preview.ItemsSource[i:]
            remaining_time = 0
            for obj in remaining_objs:
                remaining_time += obj.time_estimate
            remaining_time_min_part = int(math.floor(remaining_time / 60))
            remaining_time_sec_part = int(remaining_time % 60)
            remaining_time = "{:.2f} mins = {}m {}s".format(remaining_time / 60.0, remaining_time_min_part, remaining_time_sec_part)
            self.progress_bar.Value = i + 1
            self.progress_bar_display.Text = "{}/{}\nProcessing {}\n{}".format(int(self.progress_bar.Value),\
                                                                int(self.progress_bar.Maximum), \
                                                                file_name,
                                                                "Estimated remaining time, exluding N/A items = {}".format(remaining_time))


            if self.is_copy_folder:
                if extension == ".dwg":
                    new_contents = final_files
                else:
                    new_contents = [final_file]
                EXPORT_ACTION.dump_exported_files_to_copy_folder(self.output_folder, new_contents, self.file_id_dict, self.copy_folder_path)


            # ----- end of for loop


        # ----- after exporting ------
        self.monitor_group.Visibility, self.data_grid_preview.Visibility = self.data_grid_preview.Visibility,self.monitor_group.Visibility

        self.Topmost = False
        self.button_main.Width = 600
        self.button_main.Content = "Export Finish, Start Another Job By Reopening Exporter"
        print ("Following are the files exported this time:")
        for file in self.files_exported_for_this_issue:
            print (file)
        print ("--exported files ends")



        self.is_printing = False
        self.button_cancel_export.Visibility = self.sample_color_enabled.Visibility
        self.initiate_loading_message()
        self.update_time_estimate()




        copy_folder = self.copy_folder_path if self.is_copy_folder else None

        if self.is_export_jpg:
            primary_doc = self.active_original_doc(self.orginal_doc_name) #!!!when exporting image, the exportimage method will force activate the doc. So we need to switch back primary doc so other can be closed.(tested in 2022 and before)


        #close daocs opeeedn by API
        REVIT_APPLICATION.close_docs_by_name(names = [x.Title for x in self.docs_to_be_opened_by_API], close_all = False)




        # EA_UTILITY.set_doc_change_hook_depressed(stage = False)
        # ERROR_HANDLE.print_note("my doc change hook depress status = {}".format(EA_UTILITY.is_doc_change_hook_depressed()))

        if self.is_copy_folder:

            EXPORT_ACTION.dump_exported_files_to_copy_folder(self.output_folder, self.files_exported_for_this_issue, self.file_id_dict, copy_folder)

        if self.is_combine_pdf and not self.is_printing_interupted:
            combined_pdf_name = self.textbox_combined_pdf_name.Text
            EXPORT_ACTION.combine_final_pdf(self.output_folder, self.files_exported_for_this_issue, combined_pdf_name, copy_folder)

        if self.is_play_sound:
            SOUND.play_sound("sound_effect_mario_stage_clear.wav")




        job_time_end = time.time()
        total_time_second = int(job_time_end - job_time_start)
        total_time_min = int( total_time_second / 60 )
        print ("#"*20)
        print ("all sheets from selected revit files have been printed.\nIssue parameter = [{}]".format(self.issue_name))
        EXPORT_ACTION.print_time("Print {} sheets".format(len(self.files_exported_for_this_issue)), time_end, time_start, use_minutes = True)
        print ("#"*20)
        self.print_ranked_log()
        # ERROR_HANDLE.print_note("my doc change hook depress satus = {}".format(EA_UTILITY.is_doc_change_hook_depressed()))
        ERROR_HANDLE.print_note("###END OF TOOL###")

        time_obj = time.localtime()
        localtime = "{}-{}-{}_{}-{}-{}".format(time_obj.tm_year,
                                    time_obj.tm_mon,
                                    time_obj.tm_mday,
                                    time_obj.tm_hour,
                                    time_obj.tm_min,
                                    time_obj.tm_sec)
        self.log_file = "EnneadTab Exporter AutoSave Log_{}.html".format(localtime)
        self.log_file_path = "{}\{}".format(self.output_folder , self.log_file)
        output.save_contents(self.log_file_path)






        print ("####")
        print (self.is_sync_and_close, self.is_printing_interupted)
        print ("####")
        if self.is_sync_and_close and not self.is_printing_interupted:
            REVIT_APPLICATION.sync_and_close()
            self.Close()

        total_time_min_part = int(math.floor(total_time_second / 60))
        total_time_sec_part = int(total_time_second % 60)

        REVIT_FORMS.notification(main_text = "EnneadTab Export done.",
                                        sub_text = "Total time = {}m {}s".format(total_time_min_part, total_time_sec_part),
                                        window_title = "EnneadTab Exporter",
                                        button_name = "Close",
                                        self_destruct = 0,
                                        window_height = 300)


        ending_announcement = "enni-ed tab exporter has just finished exporting {} items after {} minutes and {} seconds.".format(len(self.files_exported_for_this_issue), total_time_min_part, total_time_sec_part)
        if self.is_send_email:
            ending_announcement += "Also, an email is scheduled to sent. Subject line: {}".format(self.email_subject_line.Text.lower().replace("ennead", "enni-ed "))
        SPEAK.speak(ending_announcement)

        if not self.is_sync_and_close:
            self.update_data_grid_preview()


        if self.is_send_email:
            safety = 0
            while True:
                safety += 1
                if os.path.exists(self.log_file, self.output_folder):
                    SPEAK.speak("Output log file saved.")
                    break

                if safety % 5 == 0:
                    SPEAK.speak("Waiting for output log file to save.")
                time.sleep(1)


                if safety > 50:
                    break
            self.email_data.update_info(self)
            self.email_data.send()
            SPEAK.speak("Email is scheduled to send.")

    def print_ranked_log(self):
        rank_list = self.data_grid_preview.ItemsSource[:]

        rank_list.sort(key = lambda x:x.time_estimate, reverse = True)
        output.print_md( "## Ranked export time below:")

        for item in rank_list:
            time = item.time_estimate
            export_item = item.format_name
            if time > 120:
                mins = int(time/60)
                output.print_md(":warning: < **{}** > use ***{}*** mins".format(export_item, mins))
            else:
                output.print_md("< **{}** > use ***{}*** seconds".format(export_item, time))



    def extension_options_changed(self, sender, args):
        #print "options_changed"
        self.is_export_dwg = self.checkbox_dwg.IsChecked
        self.is_export_pdf = self.checkbox_pdf.IsChecked
        self.is_export_jpg = self.checkbox_jpg.IsChecked
        #self.print_opt_status()
        self.update_UI_enable_status()
        self.check_all_setting_ready()

    def checkbox_additional_setting_changed(self, sender, args):
        self.is_export_view_on_sheet = self.checkbox_dwg_view_export.IsChecked
        self.is_copy_folder = self.checkbox_copy_folder.IsChecked
        self.is_play_sound = self.checkbox_play_sound.IsChecked
        self.is_combine_pdf = self.checkbox_combine_pdf.IsChecked
        self.is_sync_and_close = self.checkbox_sync_and_close.IsChecked
        self.is_send_email = self.checkbox_send_email.IsChecked

        self.update_UI_enable_status()
        self.check_all_setting_ready()


    def update_UI_enable_status(self):
        disabled_color = self.sample_color_disabled.Foreground
        enabled_color = self.sample_color_enabled.Foreground


        # DWG related enable check
        self.checkbox_dwg_view_export.IsEnabled = self.is_export_dwg
        if self.is_export_dwg:
            self.checkbox_dwg_view_export.Foreground = enabled_color
        else:
            self.checkbox_dwg_view_export.Foreground = disabled_color


        # PDF related enable check
        self.checkbox_combine_pdf.IsEnabled = self.is_export_pdf
        self.radio_button_color_by_sheet.IsEnabled = self.is_export_pdf
        self.radio_button_color_BW_globally.IsEnabled = self.is_export_pdf
        if self.is_export_pdf:
            self.checkbox_combine_pdf.Foreground = enabled_color
            self.radio_button_color_by_sheet.Foreground = enabled_color
            self.radio_button_color_BW_globally.Foreground = enabled_color
        else:
            self.checkbox_combine_pdf.Foreground = disabled_color
            self.radio_button_color_by_sheet.Foreground = disabled_color
            self.radio_button_color_BW_globally.Foreground = disabled_color

        # combined pdf UI check
        self.textbox_combined_pdf_name.IsEnabled = self.checkbox_combine_pdf.IsEnabled
        if self.is_combine_pdf:
            self.textbox_combined_pdf_name.Foreground = enabled_color
        else:
            self.textbox_combined_pdf_name.Foreground = disabled_color

        if self.copy_folder_path != "Folder Path...":
            self.button_open_copy_folder.IsEnabled = True
        else:
            self.button_open_copy_folder.IsEnabled = False



        # Email related
        self.email_receivers.IsEnabled = self.checkbox_send_email.IsChecked
        self.email_subject_line.IsEnabled = self.checkbox_send_email.IsChecked
        self.email_body.IsEnabled = self.checkbox_send_email.IsChecked
        self.checkbox_add_folder_link.IsEnabled = self.checkbox_send_email.IsChecked


    @ERROR_HANDLE.try_catch_error()
    def local_issue_para_text_changed(self, sender, args):
        self.issue = self.textbox_local_isse_para_name.Text
        if len(self.issue_name) == 0:
            self.button_main.Content = "Locally defined issue Parameter cannot be empty."
        self.update_data_grid_preview()


    def name_format_changed(self, sender, args):
        self.is_name_format_with_plotId = self.radio_button_plotId_sheetNum_sheetName.IsChecked
        self.is_name_format_with_sheetGroup = self.radio_button_sheetGroup_sheetSeries_sheetNum_sheetName.IsChecked


        self.update_data_grid_preview()


    def color_setting_changed(self, sender, args):
        self.is_color_by_sheet = self.radio_button_color_by_sheet.IsChecked

    def button_pick_docs_Clicked(self, sender, args):
        if len([doc for doc in REVIT_APPLICATION.get_top_revit_docs() if not doc.IsFamilyDocument]) > 1:
            # too many top doc
            REVIT_FORMS.dialogue(main_text = "I notice you have other document opened right now in this session.",
                                sub_text = "In order to avoid version conflicting, EnneadTab Exporter try to export opened docs only, no export from link.\n\nTo export from links, close all other files and only leave one open.")
            docs = REVIT_APPLICATION.select_top_level_docs(select_multiple = True)


        else:
            # ok, only one top doc
            docs = REVIT_APPLICATION.select_revit_link_docs(select_multiple = True, including_current_doc = True)
        if not docs:
            docs = [doc]
        self.docs_to_process = docs

        self.check_all_setting_ready()

        # update the model path pair
        self.doc_model_path_pair = dict()
        for item in self.data_grid_doc_id_map.ItemsSource:
            doc_name, id = item.doc_name, item.map_id
            self.doc_names_id_pair[doc_name] = str(id)
            self.doc_model_path_pair[doc_name] = get_doc_path(item.doc)

        #adding additional self doc data in case user are only print link, in that case we need a way to go back to original doc
        self.doc_model_path_pair[self.orginal_doc_name] = get_doc_path(doc)

    def pick_copy_folder_Clicked(self, sender, args):
        title_line = 'Pick the folder ...'
        with forms.WarningBar(title = title_line):
            folder = None
            while folder is None:
                folder = forms.pick_folder(title = title_line)
        self.folder_status_display.Content = "Folder Picked!"
        self.set_image_source(self.status_icon, "ok_icon.png")
        self.textbox_folder.Text = folder
        self.copy_folder_path = folder

        self.check_all_setting_ready()


    def show_feature_Clicked(self, sender, args):

        REVIT_FORMS.notification(main_text = "Features:",
                                        sub_text = self.feature_sum_note)
        """
        file_path = script.get_bundle_file("fix bluebeam setting.pdf")
        EA_UTILITY.try_open_app(file_path)
        output.show()
        output.print_md( "open your **bluebeam administrator**(not the bluebeam viewer)")
        print("on the printer tab, \n\t-disable 'prompt for file name'\n\t-disable 'open in viewer\n\t-Set default output folder as ('User/Documents') in 'folder option'\n\nShould look like this below.")
        img_path = script.get_bundle_file("bluebeam admin setting.png")
        output.set_height(1000)
        output.print_image(img_path)
        """

    def button_save_setting_Clicked(self, sender, args):

        self.save_setting()
        self.Close()


    def button_close_window_Clicked(self, sender, args):
        self.Close()

    def selective_export_Clicked(self, sender, args):
        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "[{}] {} - {}".format(EA_Printer_UI.central_doc_name(self.item.Document), self.item.SheetNumber, self.item.Name)

        temp = []
        for id_map_obj in self.data_grid_doc_id_map.ItemsSource:
            doc = id_map_obj.doc
            sheets = self.get_sheets_from_doc(doc)
            temp.extend(sheets)
        sheet_pool = [MyOption(x) for x in temp]
        sels = forms.SelectFromList.show(sheet_pool, name_attr = "Name", multiselect = True, title = "Select Desired Sheets")
        if sels and len(sels) < len(temp):
            self.selected_sheets = sels
            self.button_selective_export.Content = "Showing Selected Only"
        else:
            self.selected_sheets = []
            self.button_selective_export.Content = "Go Selective"
        self.update_data_grid_preview()


    def dropdown_issue_para_list_value_changed(self, sender, args):
        self.issue_name = self.issue_para_list.ItemsSource[self.issue_para_list.SelectedIndex]
        res = self.check_all_setting_ready()
        #print "after change issue dropdown, the check setting status is {}".format(res)
        #self.update_debug("after change issue dropdown, the check setting status is {}".format(res))


    def dropdown_dwg_setting_value_changed(self, sender, args):
        self.dwg_setting_name = self.dwg_setting_list.ItemsSource[self.dwg_setting_list.SelectedIndex]
        res = self.check_all_setting_ready()
        #print "after change dwg dropdown, the check setting status is {}".format(res)
        #self.update_debug("after change dwg dropdown, the check setting status is {}".format(res))

    def cancel_export_Clicked(self, sender, args):
        #print "cancel print..."
        self.button_cancel_export.Visibility = self.sample_color_enabled.Visibility
        self.is_printing = False
        self.is_printing_interupted = True

    def open_log_Clicked(self, sender, args):
        #print os.listdir(self.output_folder)
        logs = filter(lambda x:x.startswith("EnneadTab Exporter AutoSave Log"), os.listdir(self.output_folder))
        if len(logs) == 0:
            return

        logs.sort(reverse = True)
        sel = forms.SelectFromList.show(logs, multiple = False, title = "Pick a log")
        if not sel:
            return

        file = "{}\{}".format(self.output_folder, sel)
        os.startfile(file)


    def show_sample_marker_Clicked(self, sender, args):
        filepath = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\lib\MARKER.txt"
        os.startfile(filepath)
        
        
    def generate_issue_Clicked(self, sender, args):
        if not hasattr(self, "docs_to_process"):
            self.docs_to_process = [doc]
            
        issue_name = forms.ask_for_string("Sheet_$Issue_XXXX")
        
        for doc in self.docs_to_process:
            if doc.IsLinked:
                NOTIFICATION.messenger(main_text='[{}] is a link file, cannot edit.'.format(doc.Title))
                continue
            HELPER.create_issue_para_to_sheet(doc, issue_name)
        
        
        self.initiate_para_list_source()
        return
        url = "https://youtu.be/F1fp4xaewRo"
        script.open_url(url)
        main_text = "Goal: Add shared parameter 'Issue XXX' to sheet parameter."
        sub_text = "Step 1:\nCreate new shared parameter from the manager window.\n\nStep 2:\nUse the method from demo video to bind this parameter to sheet category in multiple documents"
        REVIT_FORMS.notification(main_text = main_text,
                                        sub_text = sub_text)



    def generate_print_in_color_Clicked(self, sender, args):
        if not hasattr(self, "docs_to_process"):
            self.docs_to_process = [doc]
            
        
        
        for doc in self.docs_to_process:
            if doc.IsLinked:
                NOTIFICATION.messenger(main_text='[{}] is a link file, cannot edit.'.format(doc.Title))
                continue
            HELPER.create_color_setting_to_sheet(doc)
        

        return
    
    
        url = "https://youtu.be/F1fp4xaewRo"
        script.open_url(url)
        main_text = "Goal: Add shared parameter 'Print_In_Color' to sheet parameter."
        sub_text = "Step 1:\nCreate new shared parameter from the manager window.\n\nStep 2:\nUse the method from demo video to bind this parameter to sheet category in multiple documents"
        REVIT_FORMS.notification(main_text = main_text,
                                        sub_text = sub_text)



    def open_local_folder_Clicked(self, sender, args):
        path = os.path.realpath(self.output_folder)
        os.startfile(path)


    def open_copy_folder_Clicked(self, sender, args):
        path = os.path.realpath(self.copy_folder_path)
        os.startfile(path)

    def update_doc_id_pair_Changed(self, sender, args):


        self.print_debug("pair changed.")
        self.doc_model_path_pair = dict()
        #udpate the data in the pool
        for item in self.data_grid_doc_id_map.ItemsSource:
            doc_name, id = item.doc_name, item.map_id
            #print doc_name, id
            self.doc_names_id_pair[doc_name] = str(id)
            self.doc_model_path_pair[doc_name] = get_doc_path(item.doc)

        self.check_all_setting_ready()



    def update_preview_image(self, view_or_sheet):
        EXPORT_ACTION.export_image(view_or_sheet, "EXPORTER_PREVIEW", FOLDER.get_EA_local_dump_folder(), is_thumbnail = True)
        self.set_image_source(self.preview_image, FOLDER.get_EA_dump_folder_file("EXPORTER_PREVIEW.jpg"))


    def initiate_loading_message(self):
        self.textblock_export_status.Text = "..."
        self.textblock_load_screen.Text = "..."

    def update_loading_message(self, preview_obj):
        self.textblock_export_status.Text = "{}\nEstimated time = {}".format( preview_obj.format_name, preview_obj.time_estimate_format)
        self.textblock_load_screen.Text = JOKE.random_loading_message()
    """
    !! store time 3sitmate  dict[(ID, extension)] = time

    test this, might not work for jason dump.
    """

    #def update_time_estimate(self, preview_obj, time_span):
        #preview_obj.time_estimate = time_span
        #preview_obj.time_estimate_format = "{}s".format(time_span) to convert to second or mins


    def update_time_estimate(self):

        for doc in self.docs_to_process:
            self.record = self.get_time_estimate_from_record(doc)
            for item in self.data_grid_preview.ItemsSource:
                if self.central_doc_name(item.item.Document) != self.central_doc_name(doc):
                    continue
                self.record["{}#{}".format(item.item.UniqueId, item.extension)] = item.time_estimate

            record_file = self.get_record_file_by_doc(doc)
            DATA_FILE.set_data(self.record, record_file, is_local=False)


    def get_time_estimate_from_record(self, doc):
        record_file = self.get_record_file_by_doc(doc)
        return DATA_FILE.get_data(record_file, is_local=False)



    def get_record_file_by_doc(self, doc):
        return "EXPORT_RECORD_" + self.central_doc_name(doc) + ".sexyDuck"

 
    
    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()


def get_doc_path(doc):
    if doc.IsWorkshared:
        return doc.GetWorksharingCentralModelPath()
    else:
        return doc.PathName
##################################################







@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def ennead_printer():

    # EA_UTILITY.show_loading_screen(display_text = "EnneadTab Printer is loading...", time = 2)
    window = EA_Printer_UI()
    window.ShowDialog()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    ennead_printer()
    
