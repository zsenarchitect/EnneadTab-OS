import os

from pyrevit import forms,  script
from pyrevit.revit import ErrorSwallower
from Autodesk.Revit import DB # pyright: ignore 
from Autodesk.Revit import UI # pyright: ignore

import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_UNIT, REVIT_FORMS
from EnneadTab import OUTPUT, ERROR_HANDLE, NOTIFICATION

__doc__ = """Find family file path. And remap the path to a folder you picked. In this folder, families will be organised based on their category.
This will also load the repathed families back to central model.

You have the option to sync and close after the long-boring reloading.
You also have the option to dig inside the nesting family and save them.
"""
__title__ = "Family\nRePath"
__tip__ = True
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
uiapp = UI.UIApplication



class FamilyOption(DB.IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        overwriteParameterValues = False
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        return True


class FamilyRePath:
    def __init__(self):
        self.is_failed_init = False
        self.output = script.get_output()
        self.output.close_others()
        all_families = list(DB.FilteredElementCollector(doc).OfClass(DB.Family).ToElements())
        class MyOption(forms.TemplateListItem):
            @property
            def name(self):
                return "[{}]: {}".format(self.item.FamilyCategory.Name, self.item.Name)
        all_families = [MyOption(x) for x in all_families if x]
        all_families.sort(key=lambda x: x.name)
        self.all_families = forms.SelectFromList.show(all_families, \
                                                        title = "Pick families to repath",
                                                        multiselect = True)
        if not self.all_families:
            self.is_failed_init = True
            return 
        self.collection_skip_family = []
        self.collection_not_found = []
        self.collection_BIM360_family = []
        self.collection_drive_family = []
        self.final_address = []
        self.dest_folder = forms.pick_folder(title = "Pick new folder that family should go to..")

        self.log = ""
        
        opts = [["Yes","Recursively looking for nesting family so it will take longer."], ["No","Just remap the project level family."]]
        res = REVIT_FORMS.dialogue(main_text = "Do you want to process nesting families?", 
                                                    options = opts)
        self.process_nesting = False
        if res == opts[0][0]:
            self.process_nesting = True

        
        
        opts = ["Yes", "No"]
        res = REVIT_FORMS.dialogue(main_text = "Do you want to sync Revit after families are repathed?", 
                                                    options = opts)
        self.sync_and_close = False
        if res == opts[0]:
            self.sync_and_close = True


    def is_valid_input(self):
        if not self.all_families:
            return False
        if not self.dest_folder:
            return False

        return True

    def process_families(self):
        if not self.is_valid_input():
            return

        counter = 0
        

        #with forms.ProgressBar(title = "Checking Families, Hold On...({value} of {max_value})", step = 1, cancellable = False) as pb:
        for family in self.all_families:
            try:
                indentation_title = "[{}]".format(family.Name)
                self.repath(family, indentation_title)
            except Exception as e:
                print (e)
                print ("Failed to repath: {}".format(family.Name))
            counter += 1
            #pb.update_progress(counter, len(self.all_families))

            #if pb.cancelled:
                #return

    def repath(self, family, indentation_title):
        if not family:
            return
        if not family.IsUserCreated :
            return

        if family.IsInPlace :
            print ("{} is InPlace Family. Will skip repathing.".format(family.Name))
            return
        
        if not family.IsEditable:
            return
        
        
        family_name = family.Name
        family_cate_name = family.FamilyCategory.Name
        famDoc = family.Document.EditFamily(family)
        current_path = famDoc.PathName
        family_folder = "{}\{}".format(self.dest_folder, family_cate_name)
        if not os.path.exists(family_folder):
            os.makedirs(family_folder)


        new_file_path = "{}\{}.rfa".format(family_folder, family_name)
        if current_path != new_file_path:
            try:
                family_manager = famDoc.FamilyManager
                """
                if "EA_Repath" in para_names:
                    family_manager.DeleteParameter()
                    para_name = "EA_Repath2"
                elif "EA_Repath2" in para_names:
                    family_manager.DeleteParameter()
                    para_name = "EA_Repath"
                """
                para_name = "EA_Repath"
                try:
                    para_group = DB.BuiltInParameterGroup.PG_DATA
                    para_type = DB.ParameterType.Text


                #  since 2023, ParameterType property is no longer valid.
                except:
                    para_group = DB.GroupTypeId.AdskModelProperties 
                    para_type = REVIT_UNIT.lookup_unit_spec_id("length")

                is_instance = True


                t = DB.Transaction(famDoc, "xx")
                t.Start()
                try:
                    para = family_manager.AddParameter(para_name,\
                                                        para_group,\
                                                        para_type,\
                                                        is_instance)
                except:
                    for para in family_manager.GetParameters ():

                        if para.Definition.Name == para_name:
                            break
                    family_manager.RemoveParameter (para)
                t.Commit()
                




                option = DB.SaveAsOptions ()
                option.OverwriteExistingFile = True
                famDoc.SaveAs(new_file_path, option)
                famDoc.LoadFamily(family.Document, FamilyOption())



                """
                ui_famDoc = REVIT_APPLICATION.open_and_active_project (new_file_path)
                famDoc = ui_famDoc.Document
                #out_family = clr.StrongBox[DB.Family](family)
                #famDoc.LoadFamily(doc, FamilyOption(), out_family)
                famDoc.LoadFamily(doc, FamilyOption())
                REVIT_APPLICATION.set_active_doc_as_new_family()
                famDoc.Close(False)
                #REVIT_APPLICATION.close_docs_by_name([family_name])
                #doc.LoadFamily(new_file_path)
                """
            except Exception as e:
                self.log += "\nError updating path: {}".format(e)
                self.log += "\n\n{}".format(e)

        if current_path == "":
            current_path = "Save Path Not Found"
        self.final_address.append((family_cate_name,family_name, current_path, new_file_path))
        
        
        if self.process_nesting:
            try:
                nesting_families = DB.FilteredElementCollector(family.Document).OfClass(DB.Family).ToElements()
                for nesting_family in nesting_families:
                    indentation_title += "-->[{}]".format(nesting_family.Name)
                    NOTIFICATION.messenger(main_text = "Discovering nesting family: {}".format(indentation_title))
                    # script.get_output().self_destruct(5)
                    self.repath(nesting_family)
            except:
                pass
            
        famDoc.Close(False)


    @ERROR_HANDLE.try_catch_error(is_silent=True)
    def display_results(self):
        if not self.is_valid_input():
            return

        print( "#" * 40 + "  Summary  " + "#" * 40)
        """
        print("{} skipped\n{} no path\n{} found path on BIM 360\n{} found path on disk drive".format()
            len(self.collection_skip_family),
            len(self.collection_not_found),
            len(self.collection_BIM360_family),
            len(self.collection_drive_family)
        )

        if len(self.collection_skip_family) > 0:
            print("\nFollowing families were skipped, mostly because of system family")
            for item in self.collection_skip_family:
                print("\t\t{}".format(item.Name))

        if len(self.collection_not_found) > 0:
            print("\nFollowing families have no file path found, mostly because of unsaved load")
            for item in self.collection_not_found:
                print("\t\t{}".format(item.Name))

        if len(self.collection_BIM360_family) > 0:
            self.output.freeze()
            print_collection(self.collection_BIM360_family, "BIM 360 Families")
            self.output.unfreeze()
        """
        self.final_address.sort(key = lambda x: x[1])
        self.print_collection(self.final_address)


        print (self.log)

        print ("\n\nEnd of Tool")
        NOTIFICATION.messenger(main_text = "All families have beeen remapped.")
        
        OUTPUT.display_output_on_browser()

    def print_collection(self,collection):
        # table_data = []
        # for item in collection:

        #     table_data.append(item)
        collection.sort(key = lambda x: (x[0],x[1]))
        if len(collection) > 0:
            self.output.print_table(table_data=collection, 
                                    title="Repath Family for [{}]: {} families".format(doc.Title, len(collection)), 
                                    columns=["Category","Family", "Old Path", "New Path"], 
                                    formats=["",'', '{}', '{}'],
                                    last_line_style='color:red;')
            
        script.get_output().self_destruct(1000)


def main():
    family_repath = FamilyRePath()
    if family_repath.is_failed_init:
        return

    with ErrorSwallower() as swallower:
        family_repath.process_families()
    family_repath.display_results()
    if family_repath.sync_and_close:
        REVIT_APPLICATION.sync_and_close()

        
        
        
####################################
if __name__ == "__main__":
    
    
    main()

