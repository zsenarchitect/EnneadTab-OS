#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    >>> with ErrorSwallower() as swallower:
    >>>     for fam in families:
    >>>         doc.EditFamily(fam)
    >>>         if swallower.get_swallowed():
    >>>             logger.warn("Warnings swallowed")
"""
__context__ = "zero-doc"
__doc__ = "Process all the family file to generate a metadata file for usage later."
__title__ = "MetaData\nExporter"

import os
import time

from pyrevit import script
from pyrevit import ErrorSwallower

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
import random

from EnneadTab import NOTIFICATION, TIME, ERROR_HANDLE, FOLDER, DATA_FILE, EXE, FOLDER, SOUND, ENVIRONMENT
from EnneadTab.REVIT import REVIT_UNIT, REVIT_APPLICATION, REVIT_EVENT, REVIT_EXPORT

try:
    doc = __revit__.ActiveUIDocument.Document # pyright: ignore
    uidoc = __revit__.ActiveUIDocument # pyright: ignore
except:
    pass


SAFETY_MAX =  40000
USE_RANDOM_SAMPLE = True
IS_IGNORE_EXISTING = False
          
class FamilyMetaDataExporter:
    def __init__(self):
        self.family_lib_folder =  "{}\\01_Revit\\03_Library".format(ENVIRONMENT.L_DRIVE_HOST_FOLDER)     
        self.counter = 0   
        self.meta_data_folder = "{}\\Family Browser".format(ENVIRONMENT.DB_FOLDER)
        self.opened_docs = []
        try: 
            self.initial_view = doc.ActiveView
        except:
            self.initial_view = None
        if IS_IGNORE_EXISTING:
            self.existing_meta_data = [x for x in os.listdir(self.meta_data_folder) if x.endswith(".sexyDuck")]
            # print self.existing_meta_data
            NOTIFICATION.messenger (main_text = "{} existing meta data file(s) found.".format(len(self.existing_meta_data)))
    
    @TIME.timer
    def export_data(self):
        REVIT_EVENT.set_L_drive_alert_hook_depressed(stage=True)
        
        
        self.is_dry_run = True
        # dry run to get the total family count but not process data
        self.process_folder(self.family_lib_folder)
        self.total_family_count = self.counter
        
        self.counter = 0 
        self.is_dry_run = False
        self.process_folder(self.family_lib_folder)
        
        
        print ("Meta data exported!!!!")
        SOUND.play_sound("sound effect_mario stage clear.wav")
        REVIT_EVENT.set_L_drive_alert_hook_depressed(stage= False)

        
        try: 
            self.clear_open_docs()
        except:
            pass
    
    def is_too_many_open_docs(self):
        if len(self.opened_docs) > 3:
            return True
        else:
            return False
    
    def clear_open_docs(self):
        try:
            uidoc.ActiveView = self.initial_view
        except:
            pass
        
        
        for family_doc in self.opened_docs:
            try:
                family_doc.Close(False)
                self.opened_docs.remove(family_doc)
                
            except:
                pass

    
    def process_folder(self, folder):
        if "_Archive" in folder:
            return
        
        if "_Component" in folder:
            return
        
        # here use randon sample instead of full map!!!!!!!!!
        if USE_RANDOM_SAMPLE:
            source = random.sample(os.listdir(folder), min(10, len(os.listdir(folder))))
        else:
            source = os.listdir(folder)
        for item in source:
            item_address = os.path.join(folder, item)
            
            # recusive process item if it is also a folder
            if os.path.isdir(item_address):
                self.process_folder(item_address)
            
            if not item.endswith(".rfa"):
                continue
            
            self.process_family(item_address)
            
    def process_family(self, family_path):
        self.counter += 1
        
        if IS_IGNORE_EXISTING:
            # extract the file name with extension in the file path
            
            
            
            head, tail = os.path.split(family_path)
            if tail.replace(".rfa", ".sexyDuck")  in  self.existing_meta_data:
                # NOTIFICATION.messenger (main_text = tail.replace(".rfa", ".sexyDuck"))
                # if json file modification date is within last 3 day, return func
                # this is to avoid processing the same family file again and again                
                if time.time() - os.path.getctime(family_path) < 60*60*24*3:
                    return
                
        # remove this safety lock later
        if self.counter >SAFETY_MAX :
            return
                
        if self.is_dry_run:
            return
        
        
            
        NOTIFICATION.messenger (main_text = "-{}/{}: {}".format(self.counter,self.total_family_count, 
                                                                      family_path.replace(self.family_lib_folder, ""),
                                        width = 1500))
        
        family_doc = REVIT_APPLICATION.get_application().OpenDocumentFile(family_path)
        # print family_doc
        t = DB.Transaction(family_doc, "Export Family Meta Data")
        t.Start()
        
        views = DB.FilteredElementCollector(family_doc).OfClass(DB.View).WhereElementIsNotElementType ().ToElements()
        
        meta_file_path = "{}\\{}".format(self.meta_data_folder, family_doc.Title + ".sexyDuck")
        if FOLDER.is_path_exist(meta_file_path):
            meta_data = DATA_FILE.get_data(meta_file_path)
        else:
            meta_data = dict()
            
            
        meta_data["family_name"] = family_doc.Title
        meta_data["family_category"] = family_doc.OwnerFamily.FamilyCategory.Name
        
        
        family_unit = family_doc.GetUnits()
        length_spec = REVIT_UNIT.lookup_unit_spec_id("length")
        format_option = family_unit.GetFormatOptions (length_spec)
        unit_id = format_option.GetUnitTypeId ()
        unit_string = str(unit_id)#.split("-")[0].split("unit:")[1]
        meta_data["family_unit"] = unit_string
        
        try:
            basic_info = DB.BasicFileInfo.Extract(family_path)
            meta_data["family_version"] = version_year
            version_year = basic_info.Format
        except:
            pass
        display_system =  family_doc.DisplayUnitSystem .ToString()
        meta_data["display_system"] = display_system
    
    
    
        meta_data["family_path"] = family_path
        meta_data["record_time"] = TIME.get_formatted_current_time()
        meta_data["type_data"] = dict()
        
        manager = family_doc.FamilyManager
        if not manager.Types.IsEmpty:
                
            for family_type in manager.Types:
                manager.CurrentType = family_type

                type_data = self.export_views(family_doc, views, family_type.Name)
            
                meta_data["type_data"][type_data["type_name"]] = type_data
                
        else:
            type_data = self.export_views(family_doc, views, "No Type")
        
            meta_data["type_data"][type_data["type_name"]] = type_data
            
            
        t.RollBack()
        DATA_FILE.save_dict_to_json(meta_data, 
                                              meta_file_path,
                                              use_encode = True)
        
        
        self.opened_docs.append(family_doc)
        
        #family_doc.Close(False)
        
        if self.is_too_many_open_docs():
            self.clear_open_docs()
        
    def export_views(self, family_doc, views, type_name):
        type_data = dict()
        # replace all illegal character in the type_name
        type_name = type_name.replace("/","-")
        type_name = type_name.replace("\"","in")
        type_name = type_name.replace("°","degree")
        
        type_data["type_name"] = type_name
        type_data["views"] = dict()
        for view in views:
            if view.ViewType in [DB.ViewType.ProjectBrowser,
                                DB.ViewType.Schedule]:
                continue
            
            
            try:
                view.HideCategoryTemporary (DB.ElementId(DB.BuiltInCategory.OST_Dimensions))
                view.HideCategoryTemporary (DB.ElementId(DB.BuiltInCategory.OST_Constraints))

            except Exception as e:
                print (e)
                NOTIFICATION.messenger (main_text = str(e))
                pass   
            
            
            try:
                for uiview in uidoc.GetOpenUIViews():
                    if uiview.ViewId == view.Id:
                        uiview.ZoomToFit()
                        break
                uidoc.RefreshActiveView()
            except:
                pass
            
            try:
            #if view.IsValidState(DB.PreviewFamilyVisibilityMode.On):
            
                view_mode = view.TemporaryViewModes
                view_mode.PreviewFamilyVisibility  = DB .PreviewFamilyVisibilityMode.On
            #else:
            except:
                pass
            

        
            final_image = REVIT_EXPORT.export_image(view_or_sheet = view, 
                                                                file_name = "{}#{}#{}".format(family_doc.Title,type_name, view.Name), 
                                                                output_folder= self.meta_data_folder, 
                                                                is_thumbnail = False,
                                                                resolution = 2400)
            type_data["views"][view.Name] = final_image
        return type_data
        
@ERROR_HANDLE.try_catch_error()
def family_browser():

    EXE.try_open_app("AutoCancelClicker.exe")

    with ErrorSwallower() as swallower:
    # >>>     for fam in families:
    # >>>         doc.EditFamily(fam)
    # >>>         if swallower.get_swallowed():
    # >>>             logger.warn("Warnings swallowed")
        FamilyMetaDataExporter().export_data()
    pass

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    family_browser()

