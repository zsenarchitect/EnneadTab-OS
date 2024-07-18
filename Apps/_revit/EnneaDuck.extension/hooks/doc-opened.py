import os
from datetime import date
import random

from Autodesk.Revit import DB # pyright: ignore

from EnneadTab import NOTIFICATION
from pyrevit import forms, script
from pyrevit import EXEC_PARAMS
from pyrevit.coreutils import envvars
from pyrevit.coreutils import ribbon


import EnneadTab


def log_time_sheet(doc):
    EnneadTab.LOG.update_time_sheet_revit(doc.Title)



def pop_up_window(doc):
    
    
    warning_count = len(doc.GetWarnings())
    
    
    if warning_count >= 1000:
        display_text = "Ennead Alert!!!: \nPlease consider cleaning them with Ideate Tools or Ennead 'Track Warnings'."
    elif warning_count >= 200:
        display_text = "Ennead's Reminder: \nPlease consider cleaning them with Ideate Tools or Ennead 'Track Warnings'."
    elif warning_count >= 50:
        display_text = "Ennead's Friendly Reminder: \nNice! Please keep it low by regularly cleaning them with Ideate Tools or Ennead 'Track Warnings'."
    else:
        display_text = ""
        






    try:
        active_workset_id = DB.WorksetTable.GetActiveWorksetId(doc.GetWorksetTable())
        active_workset_name = DB.WorksetTable.GetWorkset(doc.GetWorksetTable(),active_workset_id).Name
        main_text = "Your Current Active Workset:\n[{}]".format(active_workset_name)


        revit_name = str(doc.Title)
        revit_name = EnneadTab.REVIT.REVIT_HISTORY.name_fix(revit_name)
        file = script.get_universal_data_file(revit_name,file_ext = "txt")
        
        current_data = EnneadTab.REVIT.REVIT_HISTORY.read_data(file, doc)
        if current_data is None:
            data_entry = "{}:{}".format(date.today(), warning_count)
            EnneadTab.REVIT.REVIT_HISTORY.append_data(file,data_entry)
            current_data = EnneadTab.REVIT.REVIT_HISTORY.read_data(file, doc)
        
        last_item = current_data[-1]
      
        if warning_count >= 50 and last_item != None:
            main_text = "{}\n\n".format(EnneadTab.REVIT.REVIT_HISTORY.compare_data(last_item, warning_count, doc)) + main_text



        NOTIFICATION.messenger(main_text)
        # EnneadTab.REVIT.REVIT_FORMS.notification(main_text = main_text, sub_text = display_text, self_destruct = 10) # make sure this self destruct time is shorter than the script kill time defined below
        data_entry = "{}:{}".format(date.today(), warning_count)
        EnneadTab.REVIT.REVIT_HISTORY.append_data(file,data_entry)


    except Exception as e:
        print (e)
        active_workset_name = "No Workset Availible."


    output = script.get_output()
    if EnneadTab.REVIT.REVIT_EXTERNAL_FILE.get_import_CAD(doc, output):
        day_delta = warn_ignorance(doc,
                                    warning_cate="WARNING_IGNORANCE_IMPORT_CAD_RECORD")
        if day_delta > 10:
            addition_note = "Your team have been ignoring this import CAD warning for {} days.\nI will be happy if you fix it soon! Quack!".format(int(day_delta))
            EnneadTab.NOTIFICATION.messenger(main_text = addition_note, importance_level=2)
        if day_delta > 30:
            EnneadTab.EMAIL.email(receiver_email_list=["gayatri.desai@ennead.com"],
                                subject="Help!!!!!!",
                                body="I need new pair of glass becasue I cannot see very well.\n\nThere are imported CAD in the file, I have been warned for {} days but I cannot see the message well. Do you know some good optometrists?\n\nBest,\n{}".format(day_delta,
                                                                                                                                                                                                                                                                 EnneadTab.USER.get_user_name()))
    else:
        remove_ignorance(doc,
                        warning_cate="WARNING_IGNORANCE_IMPORT_CAD_RECORD")
        


@EnneadTab.ERROR_HANDLE.try_pass
def basic_info(doc):
    if EA_UTILITY.get_user_name() in ["achiHXDF8"]:
        return

    if hasattr(doc,"GetCloudModelUrn") and doc.GetCloudModelUrn () is None:
        # The document is a BIM360 project.
       
        return
        
    try:
        file_info = DB.BasicFileInfo.Extract(doc.PathName)

        #print file_info
    except:
        print ("File info cannot be extracted from the file path, might be a BIM360 project.")
  

        print ("\n# This window will close itself in {} seconds.\nYou can continue working on the project.\n\n\n".format(killtime))
        
        return
    #print file_info.IsCentral, file_info.IsCreatedLocal, file_info.IsLocal,file_info.IsWorkshared,file_info.Format, file_info.AllLocalChangesSavedToCentral
    """
    need to find out why IsCentral for a local document is also True
    """

    output = script.get_output()
    if doc.IsDetached:
        output.print_md("#This is a detached central file.")
        # forms.alert("EA Alert: \nThis is a detached central file.\nUnless you are not planning edit further, please close document right after you save it to Ennead server and create new local before any edit work.")
        EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "EA Alert: \nThis is a detached central file.", sub_text = "\nUnless you are not planning edit further, please close document right after you save it to Ennead server and create new local before any edit work.", self_destruct = 10)
        #EA_UTILITY.dialogue(icon = "warning", main_text = "EA Alert: \nThis is a detached central file.\nUnless you are not planning edit further, please close document right after you save it to Ennead server and create new local before any edit work.")


    elif file_info.CentralPath == doc.PathName:
        EA_UTILITY.dialogue(icon = "warning", main_text = "EA Alert: \nYou are working on a central model.\nIf this is not intentional, please close and creat new local.")
        # forms.alert("EA Alert: \nYou are working on a central model.\nIf this is not intentional, please close and creat new local.")
    else:
        print ("Safe, working in local.")


    lines = ["#Document Name = " + doc.Title,
             "#Central File Location = " + file_info.CentralPath,
             "#Local File location = " + doc.PathName,
             "#Latest Central Version = " + str(file_info.LatestCentralVersion)]
    for line in lines:
        try:
            output.print_md(line)
        except:
            print (line)
    
    if "1643.old" in file_info.CentralPath:
        EnneadTab.NITIFICATION.duck_pop(main_text="STOP! DO NOT WORK IN OLD FOLDER")



    print ("# This window will close itself in {} seconds.\nYou can continue working on the project.\n\n\n".format(killtime))


    

def ask_to_unload_locally(doc):

    if "2135_BiliBili SH HQ" not in doc.Title:
        return


    rvt_link_types = DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkType).ToElements()
    if len(rvt_link_types) == 0:
        return

    def are_there_unloaded_links():
        rvt_link_types = DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkType).ToElements()
        for link_type in rvt_link_types:
            print (link_type.LookupParameter("Type Name").AsString())
            #print link_type.FamilyName
            continue
            if not link_type.IsLoaded(doc, ):
                print ("not loaded")
                return True
        return False

    #print are_there_unloaded_links()
    res = EA_UTILITY.dialogue(main_text = "Team BiliBili, Do you want to locally offload links to save memory?",
                                sub_text = "This will not affect workset setting nor other people's load status, just unload for the current user",
                                options = ["Offload some links", "Keep them on"])
    if "Keep" in res or res is None:
        return


    class UnloadOption(DB.ISaveSharedCoordinatesCallbackForUnloadLocally):
        def GetSaveModifiedLinksOptionForUnloadLocally(self, rvt_link_type):
            pass
            #return False


    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return self.item.LookupParameter("Type Name").AsString()

    rvt_link_types = DB.FilteredElementCollector(doc).OfClass(DB.RevitLinkType).ToElements()
    rvt_link_types = [MyOption(x) for x in rvt_link_types]
    res = forms.SelectFromList.show(rvt_link_types,
                                    multiselect = True,
                                    title = "Which revit link to unload locally?")
    if res is None:
        return
    for link_type in res:
        try:
            link_type.UnloadLocally(UnloadOption())
        except Exception as e:
            if "for current user already"  not in str(e):
                print ("Unload locally not succesful, becasue: {}".format(e))

    # x.UnloadLocally ()

def append_sync_time_record(doc):
    script_subfolder = "Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton\\update_last_sync_datafile_script.py"
    func_name = "update_last_sync_data_file"
    EnneadTab.MODULE_HELPER.run_revit_script(script_subfolder, func_name, doc)
    
    func_name = "run_exe"
    EnneadTab.MODULE_HELPER.run_revit_script(script_subfolder, func_name)

def check_if_file_opened(doc):
    script_subfolder = "Ennead.tab\\Utility.panel\\exe_1.stack\\LAST_SYNC_MONITOR.pushbutton\\update_last_sync_datafile_script.py"
    func_name = "is_doc_opened"
    EnneadTab.MODULE_HELPER.run_revit_script(script_subfolder, func_name, doc)
    


def hide_user_tab():
    setting_file = EnneadTab.FOLDER.get_EA_dump_folder_file('revit_ui_setting.json')
    if not EnneadTab.FOLDER.is_path_exist(setting_file):
        return


    data = EnneadTab.DATA_FILE.read_json_as_dict(setting_file)

    for tab in ribbon.get_current_ui():
        #print tab.name
        #continue
        """EnneadTab_Basic
        EnneadTab_Tailor
        EnneadTab_Advanced
        EnneadTab_Beta"""

        if tab.name == "Ennead Tailor":
            # not new state since the visible value is reverse
            tab.visible = data.get("checkbox_tab_tailor", True)

        if tab.name == "Ennead Library":
            # not new state since the visible value is reverse
            tab.visible = data.get("checkbox_tab_library", True)



def register_silient_open(doc):
    #print doc.Title
    if not doc.IsModelInCloud:
        return
    if not doc.IsWorkshared :
        return
    model_path = doc.GetWorksharingCentralModelPath ()
    #print model_path.GetProjectGUID  ()
    #print model_path.GetModelGUID ()
    #print model_path.Region

    

    filepath = "{}\doc_opener.json".format(EnneadTab.ENVIRONMENT.MISC_FOLDER)

    try:
        data = EnneadTab.DATA_FILE.read_json_file_safely(filepath)
        if doc.Title in data.keys():
            return
    except:
        data = dict()
        
    # for revit 2020 and before, model_path has not attribute for region. There is no plan to include it for version so old.
    if not hasattr(model_path, 'Region'):
        return
    
    data[doc.Title] = (str(model_path.GetProjectGUID  ()),
                        str(model_path.GetModelGUID ()),
                        model_path.Region)

    try:
        EnneadTab.DATA_FILE.set_data(data, filepath)
    except:
        print ("Cannot register model due to L drive access limit.")
    #print "\n\nYour model is regiestered."



def check_if_keynote_file_pointing_to_library(doc):
    if doc.Title in ["EA_Planning_R22", 
                     "EA_Detail Standards v1.1_R22"]:
        return
    knote_table = DB.KeynoteTable.GetKeynoteTable(doc)
    #print knote_table
    if knote_table.IsExternalFileReference():
        #print "This is external file reference"

        knote_table_ref = knote_table.GetExternalFileReference()
        file_path =  DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(knote_table_ref.GetAbsolutePath())
        if "Applied Computing" in file_path:

            EnneadTab.NOTIFICATION.messenger(main_text = "Your model keynote file is pointing to Applied Computing folder.\nPlease move it to your project folder to avoid conflicting other projects!")
            
            day_delta = warn_ignorance(doc,
                                        warning_cate="WARNING_IGNORANCE_KEYNOTE_FILE_RECORD")
            if day_delta > 3:
                addition_note = "Your team have been ignoring this keynote file warning for {} days.\nI will be happy if you fix it soon! Quack!".format(int(day_delta))
                EnneadTab.NOTIFICATION.duck_pop(main_text = addition_note)
            if day_delta > 10:
                EnneadTab.EMAIL.email(receiver_email_list=["gayatri.desai@ennead.com"],
                                    subject="Help!!!!!!",
                                    body="I need new pair of glass becasue I cannot see very well.\n\nThe keynote file is pointing to the shared L drive location, I have been warned for {} days but I cannot see the message well. Do you know some good optometrists?\n\nBest,\n{}".format(day_delta,
                                                                                                                                                                                                                                                                                              EnneadTab.USER.get_user_name()))

        
    # if knote_table.RefersToExternalResourceReferences():
    #     refs = knote_table.GetExternalResourceReferences()
    #     if refs:
    #         for ref_type, ref in dict(refs).items():
    #             if ref.HasValidDisplayPath():
    #                 print ref.InSessionPath
    #                 break



def warn_ignorance(doc, warning_cate):
    ignore_list = ["gayatri.desai",
                   "achi",
                   "scott.mackenzie"]
    if EnneadTab.USER.get_user_name() in ignore_list:
        return 0
    
    
    record_file = "{}_{}.json".format(warning_cate,
                                      doc.Title)
    if not os.path.exists(record_file):
        record = dict()
    else:
        record = EnneadTab.DATA_FILE.read_json_as_dict_in_shared_dump_folder(record_file, create_if_not_exist=True)
    
    import time
    if len(record.keys()) == 0:
        record[0] = {"timestamp":time.time(),
                    "user":EnneadTab.USER.get_user_name()}
        EnneadTab.DATA_FILE.set_data_in_shared_dump_folder(record, record_file)
        return
    
    this_record_index = len(record.keys())
    record[this_record_index] = {"timestamp":time.time(),
                                "user":EnneadTab.USER.get_user_name()}
    EnneadTab.DATA_FILE.set_data_in_shared_dump_folder(record, record_file)
    
    day_delta = (time.time() - record["0"].get("timestamp"))/86400 # there is 86400 secons in one day
    return int(day_delta)

def remove_ignorance(doc, warning_cate):
    record_file = "{}_{}.json".format(warning_cate,
                                      doc.Title)
    file = EnneadTab.FOLDER.get_shared_dump_folder_file(record_file)
    if os.path.exists(file):
        os.remove(file)


def check_group_usage(doc):
    if random.random() > 0.1:
        return
    max_count = 5
    count = 0 
    output = script.get_output()
    all_group_types = DB.FilteredElementCollector(doc).OfClass(DB.GroupType).ToElements()
    for group_type in all_group_types:
        group_name = group_type.LookupParameter("Type Name").AsString()
        if "ea" in group_name.lower():
            continue
        if "enneadtab" in group_name.lower():
            continue

        # cap max ducks/msg
        if count >= max_count:
            return
        
        if group_type.Groups.Size == 0:
            count += 1
            EnneadTab.NOTIFICATION.messenger(main_text = "Group type <{}> is defined but has no instances used in the project.\nConsider purging?".format(group_name)) 
            print ("\nFound group definition but not placed in project. GroupName: {}".format(group_name))
            continue
        
        sample_group = list(group_type.Groups)[0]
        if len(list(sample_group.GetMemberIds ())) == 1:
            count += 1
            EnneadTab.NOTIFICATION.messenger(main_text = "Group type <{}> has only 1 element inside the group.\nThis is not the best use of the group.".format(group_name)) 
            
            print ("\nFound group with only 1 elements.")
            print ("Sample Group: {}".format(output.linkify(sample_group.Id, title="Sample Group Instance")))
            if hasattr(sample_group, "OwnerViewId") and sample_group.OwnerViewId != DB.ElementId.InvalidElementId:
                print ("Sample Group is in this view: {}".format(output.linkify(sample_group.OwnerViewId, title = doc.GetElement(sample_group.OwnerViewId).Name)))

            

########## main code below ############

@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():
    # this varaible is set to True only after    use sync and close all is run ealier. So if user open new docs, we shoudl resume default False,
    envvars.set_pyrevit_env_var("IS_AFTER_SYNC_WARNING_DISABLED", False)

    hide_user_tab()



    if EA_UTILITY.is_open_hook_depressed():
        print ("not running doc-opening hook")
        script.get_output().close()
        return
    else:
        EnneadTab.SOUND.play_sound("sound_effect_popup_msg1.wav")
        if EnneadTab.ENVIRONMENT.is_Revit_limited():
            return
        output = script.get_output()
        global killtime
        killtime = 90
        output.self_destruct(killtime)
        try:
            doc = EXEC_PARAMS.event_args.Document
        except:
            return

        if not doc:
            return

        if doc.IsFamilyDocument:
            return

        EnneadTab.REVIT.REVIT_HISTORY.record_warning(doc)
        log_time_sheet(doc)
        

        try:
            check_group_usage(doc)
        except SystemError:
            pass

        check_if_keynote_file_pointing_to_library(doc)


        ask_to_unload_locally(doc)
    
        check_if_file_opened(doc)
        append_sync_time_record(doc)

        #ENNEAD_LOG.open_doc_with_warning_count(warning_count = len(doc.GetWarnings()))
        basic_info(doc)
        pop_up_window(doc)
        

        
        ENNEAD_LOG.warn_revit_session_too_long(non_interuptive = True)
        
        ENNEAD_LOG.update_local_warning(doc)

        register_silient_open(doc)



    #example to make auto changes to doc continously
    """
    from EnneadTab import USER
    if not USER.is_enneadtab_developer():
        return
    from EnneadTab.REVIT import REVIT_AUTO
    

    def my_func():
        from EnneadTab.REVIT import REVIT_APPLICATION
        doc = REVIT_APPLICATION.get_doc()
        all_sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).ToElements()
        # print (len(all_sheets))
    t = DB.Transaction(doc, "temp")
    t.Start()
    for sheet in all_sheets:
        sheet.Name += "#"
    t.Commit()
    
    updater = REVIT_AUTO.RevitUpdater(my_func)
    updater.start()
    """



############################
if __name__ == "__main__":
    main()
