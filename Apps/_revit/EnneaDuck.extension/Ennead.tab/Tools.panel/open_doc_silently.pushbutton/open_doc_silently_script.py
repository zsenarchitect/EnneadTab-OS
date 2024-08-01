#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Open many docs siliently, meaning any warning will be swallowed so the opening will not be stopped, and a summery is returned at final stage.\n\nAlso support audit and no-workset opening option."
__title__ = "Open Doc(s)\nSiliently"
__context__ = "zero-doc"
__tip__ = True
from pyrevit import forms #
from pyrevit import script #


import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import DATA_FILE, ERROR_HANDLE, LOG
import System
from pyrevit.revit import ErrorSwallower
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

class Solution:
    @staticmethod
    def tuple_to_model_path(tuple):
        if not tuple:
            return

        project_guid = tuple[0]
        file_guid = tuple[1]
        region = tuple[2]
        #print project_guid, file_guid
        # region = DB.ModelPathUtils.CloudRegionUS
        #print region
        cloud_path = DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(region, System.Guid(project_guid), System.Guid(file_guid))
        return cloud_path


    def open_doc_siliently(self, doc_name):
        if doc_name not in self.data:
            print ("[{}] has not been recorded by EnneadTab before in data".format(doc_name))
            return
        
        
        cloud_path = self.tuple_to_model_path(self.data[doc_name])

        open_options = DB.OpenOptions()
        if self.open_without_workset:
            open_options.SetOpenWorksetsConfiguration (DB.WorksetConfiguration(DB.WorksetConfigurationOption.CloseAllWorksets ) )
        if self.use_audit:
            open_options.Audit = True
        try:
            __revit__.OpenAndActivateDocument (cloud_path, open_options, False)
            return
            new_doc = REVIT_APPLICATION.get_app().OpenDocumentFile(cloud_path,
                                                                                            open_options)
        except Exception as e:
            print ("{} cannot be opened becasue {}".format(doc_name, e))

    @ERROR_HANDLE.try_catch_error()
    def main(self, doc_names = None):
        if not doc_names:
        
            use_audit_res = REVIT_FORMS.dialogue(main_text = "Open with audit?", options = ["Yes", "No audit"])
            if "yes" in use_audit_res.lower():
                self.use_audit = True
            else:
                self.use_audit = False

            open_without_workset_res = REVIT_FORMS.dialogue(options = ["Yes, no worksets", "No, keep default open status"], main_text = "Open without worksets?")
            if "yes" in open_without_workset_res.lower():
                self.open_without_workset = True
            else:
                self.open_without_workset = False
        else:
            self.use_audit = False
            self.open_without_workset = False

        # TO-DO: replace with ENVIRONEMENT MISC_FOLDER
        filepath = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc\doc_opener.sexyDuck"

        self.data = DATA_FILE.get_data(filepath)

        if not doc_names:
            docs_to_process = forms.SelectFromList.show(sorted(self.data),
                                                    multiselect = True,
                                                    title = "Pick doc(s) to open siliently.")
            if not docs_to_process:
                return
        else:
            docs_to_process = doc_names

        docs_already_open = [x.Title for x in REVIT_APPLICATION.get_top_revit_docs()]
        docs_to_be_opened_by_API = [x for x in docs_to_process if x not in docs_already_open]
        print ("docs alrady open = {}".format(docs_already_open))
        print ("docs to be opened = {}".format(docs_to_be_opened_by_API))


        REVIT_APPLICATION.set_open_hook_depressed(True)
        warnings = ""
        with ErrorSwallower() as swallower:
            for doc_name in docs_to_be_opened_by_API:
                self.open_doc_siliently(doc_name)
                errors = swallower.get_swallowed_errors()
                #print errors
                if len(errors) != 0:
                    warnings += "\n\n{}".format(errors)
        print ("silent mode finish")
        for doc_name in docs_to_be_opened_by_API:
            model_path = self.tuple_to_model_path(self.data.get(doc_name, None))
            if not model_path:
                continue
            REVIT_APPLICATION.open_and_active_project(model_path)


        REVIT_APPLICATION.set_open_hook_depressed(False)


        if warnings != "":
            REVIT_FORMS.notification(main_text = "There have been some warnings ignored during opening.",
                                                    sub_text = warnings,
                                                    window_title = "EnneadTab",
                                                    button_name = "Close",
                                                    self_destruct = 60,
                                                    window_width = 800)


def open_doc_silently(doc_names):
    Solution().main(doc_names)


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def main():
    Solution().main()
    
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    main()

