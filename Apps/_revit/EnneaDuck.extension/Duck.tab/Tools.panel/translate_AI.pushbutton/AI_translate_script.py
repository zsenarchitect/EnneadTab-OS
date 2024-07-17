#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Translate sheet names, view names, and maybe one day annotations."
__title__ = "AI\nTranslate"
__post_link__ = "https://ei.ennead.com/_layouts/15/Updates/ViewPost.aspx?ItemID=29679"
__youtube__ = "https://youtu.be/7dlOneO2Mts"
__tip__ = True

from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore

from pyrevit.forms import WPFWindow
from pyrevit import script, forms

import traceback
import EnneadTab
from EnneadTab.FUN import JOKES
import System
import time
import difflib
uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = EnneadTab.REVIT.REVIT_APPLICATION.get_doc()
__persistentengine__ = True

import ENNEAD_LOG


def OLD_clock_work(window):
    current_text = window.debug_textbox.Text
    max_wait = 20
    wait = 0
    while True:
        if wait > max_wait:
            break
        wait += 1
        deco = "." * (wait % 5)
        #print deco
        if not window.simple_event_handler.OUT:
            window.debug_textbox.Text = current_text + "\n\nThinking{}".format(deco)

        else:
            window.debug_textbox.Text = window.simple_event_handler.OUT
            break
        time.sleep(1)

    window.simple_event_handler.OUT = None


def translate_contents(data, para_name):
    print ("firing... ext event")
    t = DB.Transaction(doc, "Translate")
    t.Start()

    success_count = 0
    failed_count = 0
    for item in data:
        if not item.is_approved:
            continue


        sheet = doc.GetElement(item.id)
        current_translation = sheet.LookupParameter(para_name).AsString()
        if current_translation == item.chinese_name:
            print ("Existing translation to <{}> is the same version as the approved one.".format(item.english_name))
            failed_count += 1
            continue

        print ("Adding translation to <{}>".format(item.english_name))
        if sheet.LookupParameter(para_name).IsReadOnly:
            print ("The translation parameter for {} is read-only.".format(output.linkify(sheet.Id, title = item.english_name)))
            failed_count += 1
            continue
        sheet.LookupParameter(para_name).Set(item.chinese_name)
        success_count += 1
    t.Commit()
    EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "Approved translation added to sheets.\nYou may add other sheets or exit the window.",
                                            sub_text = "{} translation added/modified.\n{} sheet skipped due to existing translation matching approved version, or tranlation parameter locked by template.".format(success_count, failed_count))


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



class DataGridObj(object):
    def __init__(self, element_id, chinese_name = None, is_approved = False):
        self.id = element_id
        element = doc.GetElement(element_id)
        if isinstance(element, DB.ViewSheet):
            self.english_name = element.Name
            self.sheet_num = element.SheetNumber
        else:
            title_para_id = DB.BuiltInParameter.VIEW_DESCRIPTION
            title = element.Parameter[title_para_id].AsString()
            if len(title) > 0:
                self.english_name = title
            else:
                self.english_name = element.Name
            self.sheet_num = element.LookupParameter("Sheet Number").AsString()

        self.chinese_name = chinese_name
        self.is_approved = is_approved


# A simple WPF form used to call the ExternalEvent
class AI_translate_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):


        #print "doing preaction"
        # Now we need to make an instance of this handler. Moreover, it shows that the same class could be used to for
        # different functions using different handler class instances
        self.revit_update_event_handler = SimpleEventHandler(translate_contents)
        #self.clock_event_handler = SimpleEventHandler(clock_work)
        # We now need to create the ExternalEvent
        self.ext_event = ExternalEvent.Create(self.revit_update_event_handler)
        #self.ext_event_clock = ExternalEvent.Create(self.clock_event_handler)
        #print "preaction done"
        #print self.revit_update_event_handler
        #print self.revit_update_event_handler.kwargs
        #print self.ext_event
        #print "-------"
        return

    def __init__(self):
        self.pre_actions()

        xaml_file_name = "AI_translate_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab AI Translator"

        self.sub_text.Text = "Use openAI to translate sheet names from English to Chinese and apply changes to Revit.\n使用 openAI 将图纸名称从英文翻译成中文，并将更改应用到 Revit。"


        self.instruction_step_text.Text = "\t-Step 1:\n\n\t-Step 2:\n\t-Step 3:\n\n\n\t-Step 4:"

        self.instruction_text.Text = "Pick sheets. For performance reason, please limit the amount of sheets to translate.\n(Recommending less than 100 sheets.)\nTranslate sheets.\nMake edits to the results by editing in the table if needed. When you are happy with some or all the result, click 'approve' checkbox to lock this version. Once approved, the Chinese part will not change if you try to run translate again.\nApply approved translation to Revit."

        self.Title = self.title_text.Text

        self.set_image_source(self.logo_img, "{}\logo_vertical_light.png".format(EnneadTab.ENVIRONMENT_CONSTANTS.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        self.translation_para_name.Text = "MC_$Translate"
        self.radial_bt_do_sheets.IsChecked = True
        self.mode = "Sheets"
        self.update_category_header()

        self.Show()




    @EnneadTab.ERROR_HANDLE.try_catch_error
    def pick_views_sheets_Click(self, sender, e):

        if not self.is_translation_para_valid():
            return

        if self.radial_bt_do_sheets.IsChecked:
            """
            DB_class = DB.ViewSheet
            all_elements = DB.FilteredElementCollector(doc).OfClass(DB_class).WhereElementIsNotElementType().ToElements()
            all_elements = list(all_elements)
            all_elements.sort(key = lambda x: x.Name)
            """
            selected_elements = forms.select_sheets(title = "Select {} to translate".format(self.mode),
                                                    button_name = "Select {} to translate".format(self.mode))


        else:
            DB_class = DB.View
            """
            elements = DB.FilteredElementCollector(doc).OfClass(DB_class).WhereElementIsNotElementType().ToElements ()
            temp = list(elements)[0:10]
            for x in  temp:
                print x.ViewType

            elements = filter(lambda x: x.ViewType == DB.ViewType.FloorPlan, elements)
            if len(elements) == 0:
                return False
            element = elements[0]
            """
            all_elements = DB.FilteredElementCollector(doc).OfClass(DB_class).WhereElementIsNotElementType().ToElements()
            all_elements = list(all_elements)


            all_elements.sort(key = lambda x: x.Name)



            def is_good_view(x):
                if x.IsTemplate:
                    return False
                if "revision schedule" in x.Name.lower():
                    return False
                if x.ViewType not in [DB.ViewType.FloorPlan,
                                DB.ViewType.CeilingPlan,
                                DB.ViewType.Elevation,
                                DB.ViewType.ThreeD,

                                DB.ViewType.DraftingView,
                                DB.ViewType.Legend,
                                DB.ViewType.AreaPlan,
                                DB.ViewType.Section,
                                DB.ViewType.Detail]:
                    return False
                return  x.LookupParameter("Sheet Number").AsString() != "---"
       

            all_elements = filter(is_good_view, all_elements)



            selected_elements = forms.SelectFromList.show(all_elements,
                                                        multiselect = True,
                                                        title = "Select {} to translate".format(self.mode),
                                                        button_name = "Select {} to translate".format(self.mode),
                                                        name_attr = "Name")





        if not selected_elements:
            return

        para_name = self.translation_para_name.Text

        def new_item(x):
            if not x.LookupParameter(para_name):
                return  DataGridObj(x.Id, chinese_name = "---", is_approved = True)

            current_translation = x.LookupParameter(para_name).AsString()

            if not current_translation or len(current_translation) == 0:
                return DataGridObj(x.Id)
            return DataGridObj(x.Id, chinese_name = current_translation, is_approved = True)
        self.data_grid.ItemsSource = [new_item(x) for x in selected_elements]
        self.data_grid.Visibility = System.Windows.Visibility.Visible

        self.bt_translate_sheet.Visibility = System.Windows.Visibility.Visible
        self.bt_apply_translation.Visibility = System.Windows.Visibility.Visible
        self.bt_open_recent.Visibility = System.Windows.Visibility.Visible
        self.bt_approve_selected.Visibility = System.Windows.Visibility.Visible
        self.bt_unapprove_selected.Visibility = System.Windows.Visibility.Visible



    @EnneadTab.ERROR_HANDLE.try_catch_error
    def translate_views_sheets_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        """dummy"""
        temp = []
        for item in self.data_grid.ItemsSource:
            if item.is_approved:
                temp.append(item)
            else:
                item.chinese_name = "translating..." + item.english_name
                temp.append(DataGridObj(item.id, item.chinese_name))

        self.data_grid.ItemsSource = temp

        """real"""
        new_prompt = ""
        lookup_map = []

        for item in self.data_grid.ItemsSource:
            if not item.is_approved:
                new_prompt += "\n{} >> ?".format(item.english_name)
                lookup_map.append(item.english_name)


        if len(lookup_map) == 0:
            self.debug_textbox.Text = "There is nothing to translate."
            EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "There is nothing to translate.", sub_text = "Everything is approved.")
            return

        result = self.fire_AI_translator(new_prompt, len(lookup_map))


        #print "%%%%%%%%%%%%%%%%%%%%"
        #print lookup_map
        #print result
        if not result:
            return
        """
        result should be long string xxxx>aaaa\nyyyyy>>bbb\n
        """
        data = dict()
        self.recent_translation = ["##Below are the recent translations, you can pick to copy-paste into the Translator Table."]
        #print "===========   start to diguest  ======="
        index = 0
        for line in result.split("\n"):
            line = line.replace("Translator:", "")
            print (line)
            if ">>" not in line:
                continue

            try:
                english, chinese = line.split(">>")
            except:
                continue
            
            # add backup   translation
            self.recent_translation.append(chinese.lstrip())
            
            
            english, chinese = english.strip(), chinese.strip()
            if english == chinese:
                data[lookup_map[index]] = chinese
            elif english.replace(" ", "") == chinese.replace(" ", ""):
                data[lookup_map[index]] = chinese
            elif difflib.SequenceMatcher(None, english, chinese).ratio() > 0.8:
                data[lookup_map[index]] = chinese
            else:
                data[english] = chinese
            index += 1


        temp = []
        failed_count = 0
        success_count = 0
        for item in self.data_grid.ItemsSource:
            if item.is_approved:
                temp.append(item)
            else:
                if data.has_key(item.english_name):
                    item.chinese_name = data[item.english_name]
                    temp.append(DataGridObj(item.id, item.chinese_name))
                    success_count += 1
                else:
                    print ("---Cannot find this key {}".format(item.english_name))
                    temp.append(DataGridObj(item.id, "Skipped Translation"))
                    failed_count += 1

        self.data_grid.ItemsSource = temp
        if failed_count:
            self.debug_textbox.Text = "It seems some of the items are not translated, you can ask to translate again.\nNote: It might be helpful to limit the amount of translation by approving as you iterate."
            EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "Translation success = {}\nTranslation skipped = {}\nDon't worry.".format(success_count, failed_count), sub_text = "You can ask to translate again.\nThis time, it might be helpful to limit the amount of translation by approving the ones you like so far as you iterate. This put less pressure on the AI.")


    @EnneadTab.ERROR_HANDLE.try_catch_error
    def is_translation_para_valid(self):
        para_name = self.translation_para_name.Text

        if self.radial_bt_do_sheets.IsChecked:
            DB_class = DB.ViewSheet

        else:
            DB_class = DB.ViewPlan

        element = DB.FilteredElementCollector(doc).OfClass(DB_class).WhereElementIsNotElementType().FirstElement ()


        if not element.LookupParameter(para_name):
            EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "Cannot find parameter with this name.",
                                                    sub_text = "Are you sure <{}> if a valid parameter for sheets? You can modify what is used to store translation in the lower-right textbox".format(para_name))
            return False
        return True

    #@EnneadTab.ERROR_HANDLE.try_catch_error
    def apply_translation_Click(self, sender, e):
        para_name = self.translation_para_name.Text

        if not self.is_translation_para_valid():
            return



        self.revit_update_event_handler.kwargs = self.data_grid.ItemsSource, para_name
        self.ext_event.Raise()
        res = self.revit_update_event_handler.OUT
        if res:
            self.debug_textbox.Text = res
        else:
            self.debug_textbox.Text = "Debug Output:"


    def open_recent_Click(self, sender, e):
        if not hasattr(self, "recent_translation"):
            EnneadTab.NOTIFICATION.messenger(main_text = "No recent translation found.")
            return
        
        filepath = EnneadTab.FOLDER.get_EA_dump_folder_file("EA Recent Translation.txt")
        EnneadTab.DATA_FILE.save_list_to_txt(self.recent_translation, filepath, end_with_new_line = False, use_encode = False)
        import os
        os.startfile(filepath)


    def approve_selected_Click(self, sender, e):
        self.change_approve_selected(as_approve = True)

    def unapprove_selected_Click(self, sender, e):
        self.change_approve_selected(as_approve = False)

    def change_approve_selected(self, as_approve):


        temp = []
        for i, item in enumerate(self.data_grid.ItemsSource):
            if item in self.data_grid.SelectedItems:
                approve = as_approve
            else:
                approve = item.is_approved
            temp.append( DataGridObj(item.id, item.chinese_name, approve))
        self.data_grid.ItemsSource = temp

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def change_UI_translate_mode(self, sender, e):


        if "sheets" in self.radial_bt_do_sheets.Content.lower() and self.radial_bt_do_sheets.IsChecked:
            # nothing changed
            return

        if "views" in self.radial_bt_do_sheets.Content.lower() and not self.radial_bt_do_sheets.IsChecked:
            # nothing changed
            return


        if self.radial_bt_do_sheets.IsChecked:
            self.mode = "Sheets"

        else:
            self.mode = "Views"

        self.bt_pick.Content = "Pick {}".format(self.mode)
        self.bt_translate_sheet.Content = "  Translate UnApproved {}  ".format(self.mode)
        self.bt_apply_translation.Content = "  Applied Approved Translation To {}  ".format(self.mode)
        self.data_grid.ItemsSource = []

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def change_UI_sample_category(self, sender, e):
        if self.is_include_sample_systems.IsChecked:
            self.is_include_sample_plans.IsChecked = True
            self.is_include_sample_elevations.IsChecked = True
            self.is_include_sample_sections.IsChecked = True


        if self.is_include_sample_G_series.IsChecked:
            self.is_include_sample_schedules.IsChecked = True

        self.update_category_header()

    def update_category_header(self):
        samples = self.get_sample_translation_dict()

        count = 0
        for key,value in samples.items():
            if key == "xxx":
                continue
            count += 1
        self.category_header.Text = "Limit your sample translation can help increase capacity. Current Sample: {}".format(count)


    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()

    @EnneadTab.ERROR_HANDLE.try_catch_error
    def selective_user_sample_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        samples = self.get_sample_translation_dict_from_user(use_predefined = False)
        if not samples:
            return

        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "{} >> {}".format(self.item, samples[self.item])
        opts = [MyOption(x) for x in samples.keys()]
        opts.sort(key = lambda x: x.name)
        selected = forms.SelectFromList.show(opts,
                                            multiselect = True,
                                            title = "Pick other approved translation")
        if not selected:
            self.user_samples = samples
            return

        self.user_samples = dict()
        for key in selected:
            self.user_samples[key] = samples[key]




    def get_api_key(self):

        file_path = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc\EA_API_KEY.json"



        data = EnneadTab.DATA_FILE.read_json_as_dict(file_path)
        return data["translator_api_key"]

    #@EnneadTab.ERROR_HANDLE.try_catch_error
    def fire_AI_translator(self, new_prompt, request_count):

        session_token = self.get_api_key()



        human_name = "You: "
        #print human_name

        file_name = "EA_TRANSLATE.json"
        #print file_name

        dump_folder = EnneadTab.FOLDER.get_EA_local_dump_folder()

        #print dump_folder
        file_path = "{}\{}".format(dump_folder, file_name)
        #print file_path



        data = dict()
        data["ai_name"] = "EA_Translator: "
        data["human_name"] = human_name
        data["session_token"] = session_token
        data["max_tokens"] = 1500


        sample_translate = ""

        if True:
            samples = self.get_sample_translation_dict()
            for key,value in samples.items():
                if key == "xxx":
                    continue
                sample_translate += "\n{} >> {}".format(key, value)

        if self.is_including_user_sample.IsChecked:
            user_samples = self.get_sample_translation_dict_from_user()
            for key,value in user_samples.items():
                sample_translate += "\n{} >> {}".format(key, value)

        data["key_prompt"] = u"The following is a human and translator conversation for translating professional architecture drawings names from English to Chinese. The translator is called 'Translator'. The format used here is 'English >> 中文翻译'. Here are some examples:\n{}\nPlease return the results as similar format as the 'English >> 中文翻译'\n\n\n".format(sample_translate)
        data["conversation_history"] = "{} Human: Contents to translate as below:\n{}".format(data["key_prompt"], new_prompt)
        data["direction"] = "input"

        #print data["conversation_history"]




        EnneadTab.DATA_FILE.save_dict_to_json(data, file_path, use_encode = True)

        run_exe()


        max_attempt = 90
        attempt = 0
        output.set_width(100)
        output.set_height(100)
        while True:
            print (attempt)
            if attempt % 5 == 0:
                try:
                    loading_message = "\n{}".format(JOKES.random_loading_message())
                except Exception as e:
                    print (e)
                    loading_message = ""
            self.debug_textbox.Text =  "{}s/{}s Thinking{}Max thinking time {} seconds.{}".format(attempt, max_attempt, attempt * ".", max_attempt, loading_message)

            if attempt >= max_attempt:
                self.debug_textbox.Text = "Cannot get response from the EnneadTab Server."
                EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "AI translation times out. The number of translation exceed allowed number.", sub_text = "Current translation request = {}\n\nConsider reducing the number of things to translate.".format(request_count))
                break
            attempt += 1
            time.sleep(1)
            try:
                record = EnneadTab.DATA_FILE.read_json_as_dict(file_path, use_encode = True)
            except Exception as e:
                print (e)

            if record["direction"] == "output":
                #print record["conversation_history"].split(record["key_prompt"])[-1]
                #print "Figured out!!!!!!!!!!!!!!"
                EnneadTab.SOUNDS.play_sound("sound effect_popup msg3.wav")
                self.debug_textbox.Text = "Translation finished. AI thinking time = {}s".format(attempt)
                #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                #print record["conversation_history"]
                #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
                output.set_width(500)
                output.set_height(800)
                return record["conversation_history"].split(new_prompt)[-1]

    def get_sample_translation_dict_from_user(self, use_predefined = True):
        if use_predefined and hasattr(self, "user_samples"):
            return self.user_samples

        if not self.data_grid.ItemsSource:
            return

        samples = dict()
        for item in self.data_grid.ItemsSource:
            if item.is_approved and len(item.chinese_name) != 0:
                samples[item.english_name] = item.chinese_name
        return samples


    def get_sample_translation_dict(self):
        sample_type_g_series = self.is_include_sample_G_series.IsChecked
        sample_type_schedules = self.is_include_sample_schedules.IsChecked
        sample_type_floor_plans = self.is_include_sample_plans.IsChecked
        sample_type_floor_plans_additional = self.is_include_sample_plans_additional.IsChecked
        sample_type_elevations = self.is_include_sample_elevations.IsChecked
        sample_type_elevations_additional = self.is_include_sample_elevations_additional.IsChecked
        sample_type_sections = self.is_include_sample_sections.IsChecked
        sample_type_systems = self.is_include_sample_systems.IsChecked
        sample_type_systems_additional = self.is_include_sample_systems_additional.IsChecked
        sample_type_geo_plans = self.is_include_sample_geo_plans.IsChecked
        sample_type_details = self.is_include_sample_details.IsChecked
        sample_type_rcps = self.is_include_sample_rcps.IsChecked
        sample_type_miscs = True


        samples = dict()

        #basic syntax
        #samples["SITE"] = u"场地"




        if sample_type_g_series:
            samples["COVER SHEET"] = u"封面"
            samples["NARRATIVE"] = u"设计说明"
            samples["RENDERING"] = u"效果图"
            samples["MATERIAL INDEX"] = u"材料列表"
            samples["SITE CIRCULATION ANALYSIS"] = u"场地动线分析图"
            samples["FRONTAGE RATIO"] = u"贴线率"



        if sample_type_schedules:
            samples["DRAWING LIST"] = u"图纸目录"


        if sample_type_floor_plans:
            samples["N3 - LEVEL 10 & 11 REFUGE FLOOR PLAN"] = u"建筑N3十层与十一层避难层平面图"
            samples["BASEMENT LEVEL 2 FLOOR PLAN"] = u"地下二层平面图"
            samples["Ground Floor Plan"] = u"首层平面图"
            samples["OVERALL SITE PLAN"] = u"总平面"
            samples["OVERALL 2 FLOOR PLAN"] = u"二层总体平面图"
            samples["LEVEL 5 & 6  FLOOR PLAN"] = u"五及六层平面图"
            samples["MEP ROOF FLOOR PLAN & ROOF PLAN"] = u"屋顶机房及屋顶平面图"


        if sample_type_floor_plans_additional:
            samples["N3 - MEP ROOF PLAN & ROOF PLAN"] = u"建筑N3屋顶机房平面图"
            samples["N5 - LEVEL 22 & 23  FLOOR PLAN"] = u"建筑N5二十二层与二十三层平面图"
            samples["LEVEL 26 - 28 FLOOR PLAN"] = u"二十六至二十八层平面图"
            samples["FLOOR PLAN - ROOF/MEZZANINE LEVEL"] = u"屋顶及夹层平面图"
            samples["B1 FIRE COMPARTMENT PLAN"] = u"B1防火分隔平面图"


        if sample_type_elevations:
            samples["ELEVATIONS EAST & WEST"] = u"东，西立面图"
            samples["N3 - ELEVATION EAST"] = u"建筑N3 东立面图"
            samples["SITE ELEVATIONS EAST & WEST"] = u"场地东，西立面图"
            samples["N3 - PARTIAL ELEVATIONS - TOWER"] = u"建筑N3 塔楼局部立面图"

        if sample_type_elevations_additional:
            samples["N3 - PARTIAL ELEVATIONS - PODIUM"] = u"建筑N3 裙楼局部立面图"
            samples["Enlarged Elevation"] = u"放大立面图"


        if sample_type_sections:
            samples["N3 - SECTION E-W"] = u"建筑N3 东，西剖面图"
            samples["SECTION"] = u"剖面图"

        if sample_type_geo_plans:
            samples["GEOMETRY PLAN - LEVEL 1"] = u"几何定位图首层"
            samples["GEOMETRY PLAN - ROOF/MEZZANINE LEVEL"] = u"几何定位图屋顶及夹层"
            samples["GEOMETRY PLAN - LEVEL 10,12,13,14"] = u"建筑几何定位图 十层、十二至十四层"
            samples["GEOMETRY PLAN - LEVEL 15,16,17,18"] = u"建筑几何定位图 十五至十八层"

        if sample_type_systems:
            samples["CW-1 SYSTEM DRAWINGS"] = u"主立面CW-1外墙系统"
            samples["CW-2 RECESS FACADE DETAILS TYP"] = u"CW-2退面幕墙系统详图"
            samples["CW-1 & CW-2 ENLARGED DRAWINGS - PARAPET"] = u"CW-1与CW-2幕墙系统－女儿墙"
            samples["SF-1 ENLARGED DRAWINGS - SUNKEN PLAZA"] = u"沿街立面SF－1幕墙系统下沉广场"
            samples["SKY-1 ENLARGED DRAWINGS - SKYLIGHTS"] = u"SKY－1天窗系统"
            samples["N4 - TOWER CW-1 SYSTEM DRAWINGS"] = u"建筑N4塔楼CW-1主立面外墙系统"
            samples["PODIUM CW-5/CW-5A SYSTEM DRAWINGS"] = u"裙楼CW-5/CW-5A 主立面外墙系统"

        if sample_type_systems_additional:
            samples["CW-2 PARTIAL PERSPECTIVE"] = u"CW-2 局部透视图"
            samples["CW-4A ENLARGED PLAN - LEVEL 8"] = u"CW-4A 放大平面 - 八层平面"
            samples["CW-7A ENLARGED SECTION"] = u"CW-7A 放大剖面"
            samples["CW-5A ENLARGED PLAN - TRANSITION TO CW-4"] = u"CW-5A 放大平面 - 与CW-4交接口"
            samples["SUNKEN COURTYARD ENLARGED REFLECTED CEILING PLAN"] = u"下沉广场放大吊顶平面"
            samples["RETAIL SE ENTRY SF-1 ENLARGED SECTION"] = u"商业东南入口放大剖面"
            samples["SKY-1 ENLARGED NORTH ELEVATION"] = u"采光天窗-1 放大北立面"
            samples["xxx"] = u"xxx"
            samples["xxx"] = u"xxx"
            samples["xxx"] = u"xxx"
            samples["xxx"] = u"xxx"
            samples["xxx"] = u"xxx"




        if sample_type_details:
            samples["SKY-1 & MP-6 FACADE DETAILS"] = u"天窗SKY-1及金属板MP-6幕墙系统详图"
            samples["CANOPY/VESTIBULE FACADE DETAILS"] = u"雨棚及门厅详图"
            samples["ENTRANCE FACADE DETAILS"] = u"入口幕墙节点"
            samples["CW-3 FACADE DETAILS TYP"] = u"CW-3外幕墙系统详图"
            samples["ST-1 FACADE DETAILS"] = u"ST－1主幕墙石墙系统详图"
            samples["CW-5A ENLARGED PLAN - TRANSITION TO CW-4"] = u"CW-5A 放大平面 - 与CW-4交接口"
            samples["CW-1 TYP. SLAB EDGE"] = u"CW-1 板边标准节点"
            samples["TYP. BALCONY DETAIL @ DEPRESSED SLAB"] = u"降板区标准露台节点"
            samples["GLASS LOUVER @ REFUGE FLOOR"] = u"避难层玻璃百页"
            samples["TYP. PARAPET COPING DETAIL"] = u"女儿墙顶部标准节点"
            samples["CW-3 GLASS FIN PLAN DETAIL@ LEVEL 1 LOBBY"] = u"CW-3 首层大堂弧面转角处玻璃肋平面节点"
            samples["PLAN DETAIL @ TYP. GUARDRAIL"] = u"CW-4 标准栏杆平面节点"
            samples["ST-1 PLAN DETAIL @ EGRESS DOOR"] = u"ST-1 疏散门平面节点"



        if sample_type_rcps:
            samples["LEVEL 1 & 2 RCP"] = u"反射吊顶平面一二层"
            samples["LEVEL 1 REFLECTED CEILING PLAN"] = u"一层反射天花平面"
            samples["SUNKEN COURTYARD ENLARGED REFLECTED CEILING PLAN"] = u"下沉广场放大吊顶平面"

        if sample_type_miscs:
            samples["POWER STATION DRAWINGS"] = u"变电站图纸"
            samples["RAMP AND SUPPORT"] = u"坡道及支撑件"


        return samples


        samples["xxx"] = u"xxx"

def run_exe():
    exe_location = r"L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\Project Settings\Exe\EA_TRANSLATOR\EA_TRANSLATOR.exe - Shortcut"


    try:
        EnneadTab.EXE.open_file_in_default_application(exe_location)

    except Exception as e:
        print ("$$$$$$$$$$$$$")
        print (e)








################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    # Let's launch our beautiful and useful form !

    modeless_form = AI_translate_ModelessForm()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)
