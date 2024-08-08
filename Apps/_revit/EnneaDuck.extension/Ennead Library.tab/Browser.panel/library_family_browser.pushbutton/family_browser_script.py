#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "A floating window that can help you search the family from AppliedComputing Library.\n\nDisclaimer: EnneadTab only help you find the family, but is not participating in the creation and maintainance of the family library."
__title__ = "Family\nBrowser"


from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.Exceptions import InvalidOperationException
from pyrevit.forms import WPFWindow
# from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import os

import System
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab import ENVIRONMENT
import traceback
from Autodesk.Revit import DB # pyright: ignore 

from Autodesk.Revit import UI # pyright: ignore
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
__persistentengine__ = True


@EnneadTab.ERROR_HANDLE.try_catch_error()
def load_family(family_path):
    app = doc.Application
    family_doc = app.OpenDocumentFile (family_path)
    
    family_doc.LoadFamily(doc,FamilyOption())
    



class FamilyOption(DB.IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        #update_log( "#Normal Family Load option")
        #update_log( "is family in use?: {}".format(familyInUse))
        overwriteParameterValues = True# true means use project value
        #update_log( "is overwriteParameterValues?: {}".format(overwriteParameterValues))
        #update_log( "should load")
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        #update_log( "#Shared Family Load option")
        #update_log( "is family in use?: {}".format(familyInUse))
        overwriteParameterValues = True
        #update_log( "is overwriteParameterValues?: {}".format(overwriteParameterValues))


        source = DB.FamilySource.Family
        #source = DB.FamilySource.Family
        #update_log( "is shared component using family or project definition?: {}".format(str(source)))
        #update_log( "should load")
        return True

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



class DataGrid_Preview_Obj(object):



    def __init__(self, type_meta_data):
     
        self.data = type_meta_data
        self.family_name = type_meta_data.get("family_name", "N/A")
        self.family_path = type_meta_data.get("family_path", "N/A")
        self.shortened_family_path = self.family_path.split("03_Library\\")[1]
        self.type_name = type_meta_data.get("type_name", "N/A")
        self.type_data = type_meta_data.get("type_detail", "N/A")
        self.preview_images = [x for x in type_meta_data.get("type_detail", "N/A").get("views", "N/A").values()]
        self.record_time = type_meta_data.get("record_time", "N/A")
        # print self.type_data
        
    @property
    def searcher_name(self):
        return self.family_name + "_" + self.type_name + "_" + self.shortened_family_path
        



# A simple WPF form used to call the ExternalEvent
class family_browser_ModelessForm(WPFWindow):
    """
    Simple modeless form sample
    """

    def pre_actions(self):
        

        self.load_family_event_handler = SimpleEventHandler(load_family)
        self.ext_event_load_family = ExternalEvent.Create(self.load_family_event_handler)

        pass

    def __init__(self):
        self.pre_actions()

        xaml_file_name = "family_browser_ModelessForm.xaml" ###>>>>>> if change from window to dockpane, the top level <Window></Window> need to change to <Page></Page>
        WPFWindow.__init__(self, xaml_file_name)

        self.title_text.Text = "EnneadTab Family Browser"

        self.sub_text.Text = "Find the family located at L drive library with a search bar. The result are ranked by direct name and then partial match, and then anything mentioned in the folder structure."


        self.Title = self.title_text.Text

        self.set_image_source(self.logo_img, "{}\logo_vertical_light.png".format(EnneadTab.ENVIRONMENT.CORE_IMAGES_FOLDER_FOR_PUBLISHED_REVIT))
        self.set_image_source(self.monitor_icon, "monitor_icon.png")
        self.set_image_source(self.preview_image, "DEFAULT PREVIEW_CANNOT FIND PREVIEW IMAGE.png")
        self.set_image_source(self.status_icon, "update_icon.png")


        self.meta_data_folder = "{}\\01_Revit\\06_DB\\Family Browser".format(ENVIRONMENT.HOSTER_FOLDER)



        self.data_pool = [DataGrid_Preview_Obj(x) for x in self.get_meta_datas()]

        self.data_grid.ItemsSource = self.data_pool[:]




        self.Show()

    def get_meta_datas(self):
        meta_data_files = ["{}\{}".format(self.meta_data_folder, x) for x in os.listdir(self.meta_data_folder) if x.endswith(".sexyDuck")]
        meta_data_files.sort()
        EnneadTab.NOTIFICATION.messenger(main_text = "Indexing {} files from the DataBase...\nthis might takes a few seconds...".format(len(meta_data_files)))

        family_datas =  [EnneadTab.DATA_FILE.get_data(x) for x in meta_data_files]
        type_datas = []
        for family_data in family_datas:

            for family_type in  family_data.get("type_data", []):
                temp_data = dict()
  
                temp_data["family_name"] = family_data.get("family_name", "N/A")
                temp_data["family_path"] = family_data.get("family_path", "N/A")
                temp_data["record_time"] = family_data.get("record_time", "N/A")
                temp_data["type_name"] = family_type
                temp_data["type_detail"] = family_data.get("type_data", None).get(family_type,None)
                type_datas.append(temp_data)
        
            # temp_data = family_data.get("type_data", None)
            # if temp_data is not None:
            #     try:
            #         print "\n"
            #         EnneadTab.DATA_FILE.pretty_print_dict(temp_data)
            #     except:
            #         print "!!!!!!!!!!!!!!!!!!!!!!!!!!"*100
            #         print family_data.get("family_name", "N/A")
            
        #type_datas = [EnneadTab.DATA_FILE.get_data(x) for x in meta_data_files]
        
        return type_datas


  



    @EnneadTab.ERROR_HANDLE.try_catch_error()
    def preview_selection_changed(self, sender, e):
        if len(self.data_grid.ItemsSource) == 0:
            return

        obj = self.data_grid.SelectedItem
        
        if not obj:
            
            return

        try:
            #preview_image = "{}\{}.jpg".format(self.output_folder, obj.view.UniqueId)
            preview_images = self.get_true_preview_images(obj)
            
            # create many WPF image objects, the same count as the count of preview_images
            
            self.img_viewer_panel.Children.Clear()
            
            for preview_image in preview_images:

                image = System.Windows.Controls.Image()
                bitmap = System.Windows.Media.Imaging.BitmapImage()
                bitmap.BeginInit()
                bitmap.UriSource = System .Uri(System.IO.Path.GetFullPath(preview_image))
                bitmap.EndInit()

                # Set max width for image
                
                image.MaxWidth  = 600
                image.Source = bitmap
                image.Stretch = System.Windows.Media.Stretch.Uniform
                image.Margin = System.Windows.Thickness(10)

                self.img_viewer_panel.Children.Add(image)
      
                #self.set_image_source(self.preview_image, preview_image)
                
                # hide self.preview_image, set visibility as collapese
                self.preview_image.Visibility = System.Windows.Visibility.Collapsed
                

            # creation_time = time.ctime(os.path.getctime(preview_image))
            note = "Family Name = {}\nType Name = {}\nFile Path = {}\nPreview Generated: {}".format(obj.family_name,obj.type_name, obj.shortened_family_path, obj.record_time)
            self.textblock_export_status.Text = note
        except:
            #self.update_preview_grid()
            print (traceback.format_exc())
            self.preview_image.Visibility = System.Windows.Visibility.Visible
            self.set_image_source(self.preview_image, "DEFAULT PREVIEW_CANNOT FIND PREVIEW IMAGE.png")
            self.textblock_export_status.Text = ""

    @EnneadTab.ERROR_HANDLE.try_catch_error()
    def UI_changed(self, sender, e):
        self.update_preview_grid()

    @EnneadTab.ERROR_HANDLE.try_catch_error()
    def refresh_table_Click(self, sender, e):
        self.update_preview_grid()
        self.debug_textbox.Text = "Currently showing {} views.".format(len(self.data_grid.ItemsSource))

    @EnneadTab.ERROR_HANDLE.try_catch_error()
    def update_preview_grid(self):
        if not hasattr(self, "_search_results"):
            self._search_results = []
        if len(self._search_results) != 0:
            self.data_grid.ItemsSource = self._search_results
        else:
            self.data_grid.ItemsSource = self.data_pool
        

    @EnneadTab.ERROR_HANDLE.try_catch_error()
    def open_view_click(self, sender, e):
        obj = self.data_grid.SelectedItem
        if not obj:
            return
        if not obj.view:
            self.update_preview_grid()
            return
        uidoc.ActiveView = obj.view
        pass

  

    def get_true_preview_images(self, preview_obj):
        
        preview_images = ["{}\{}".format(self.meta_data_folder, img) for img in preview_obj.preview_images]
        return preview_images

   





    #@EnneadTab.TIME.timer
    def set_search_results(self, *collections):
        """Set search results for returning."""
        self._result_index = 0
        self._search_results = []


        for resultset in collections:
            self._search_results.extend(sorted(resultset))

        temp = []
        for x in self._search_results:
            if x not in temp:
                temp.append(x)
        self._search_results = temp
        
        # print temp





    #@EnneadTab.TIME.timer
    def find_direct_match(self, input_text):
        """Find direct text matches in search term."""
        results = []
        if input_text:
            for preview_obj in self.data_pool:
                if preview_obj.searcher_name.lower().startswith(input_text):
                    results.append(preview_obj)

        return results

    #@EnneadTab.TIME.timer
    def find_word_match(self, input_text):
        """Find direct word matches in search term."""
        results = []
        if input_text:
            cur_words = input_text.split(' ')
            for preview_obj in self.data_pool:
                if all([x in preview_obj.searcher_name.lower() for x in cur_words]):
                    results.append(preview_obj)

        return results

    #@EnneadTab.TIME.timer
    def NOT_IN_USE_find_in_doc_match(self, input_text):
        """Find direct word matches in search term."""
        def has_keyword_in_doc(command_name, keywords):
            doc_string = self.search_datas[command_name][0]

            if not doc_string:
                return False

            for keyword in keywords:

                if keyword.lower() in doc_string.lower():
                    #print keyword
                    #print doc_string
                    return True
            return False

        results = []
        if input_text:
            cur_words = input_text.split(' ')
            for command_name in self._search_data_keys:
                if has_keyword_in_doc(command_name, cur_words):
                    results.append(command_name)

        return results


    def clear_search_click(self, sender, e):
        self.search_textbox.Text = ""

    @EnneadTab.ERROR_HANDLE.try_catch_error()
    def search_box_value_changed(self, sender, args):
        """Handle text changed event."""



        #import System
        if len(self.search_textbox.Text) == 0:
            self._search_results = []
        else:
            


            direct_match_results = self.find_direct_match(self.search_textbox.Text)
            word_results = self.find_word_match(self.search_textbox.Text)
            self.set_search_results(direct_match_results, word_results)
            #in_doc_results = self.find_in_doc_match(self.search_textbox.Text)
            #self.set_search_results(direct_match_results, word_results, in_doc_results)

            #print self._search_results


        self.update_preview_grid()


    @EnneadTab.ERROR_HANDLE.try_catch_error()
    def load_family_click(self, sender, e):
        if len(self.data_grid.ItemsSource) == 0:
            return

        obj = self.data_grid.SelectedItem
        
        if not obj:
            
            return
        self.load_family_event_handler.kwargs = obj.family_path,
        self.ext_event_load_family.Raise()

    def close_Click(self, sender, e):
        # This Raise() method launch a signal to Revit to tell him you want to do something in the API context
        self.Close()

    def mouse_down_main_panel(self, sender, args):
        #print "mouse down"
        sender.DragMove()




################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    
    family_browser_ModelessForm()
       

