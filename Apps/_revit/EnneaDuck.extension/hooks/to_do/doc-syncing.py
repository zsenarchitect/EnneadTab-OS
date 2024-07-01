from pyrevit import EXEC_PARAMS, script
from Autodesk.Revit import DB # pyright: ignore
import EA_UTILITY
import EnneadTab
import ENNEAD_LOG
doc = EXEC_PARAMS.event_args.Document
from pyrevit.coreutils import envvars

from EnneadTab import VERSION_CONTROL



def check_sync_queue():
    """
    return True is sync can go
    return False is sync have been stopped
    """

    log_file = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Sync_Queue\Sync Queue_{}.queue". format(doc.Title)
  
    try:
        with open(log_file, "r"):
            pass
    except:
        with open(log_file, "w+"): # if not existing then create
            pass
    queue = EA_UTILITY.read_txt_as_list(log_file)
    wait_num = len(queue)
    time = EA_UTILITY.get_formatted_current_time(show_user_name = False, use_unix_time = True)
    user_name = EnneadTab.USER.get_user_name()

    # define default value for succeful sync
    envvars.set_pyrevit_env_var("IS_SYNC_CANCELLED", False)

    data = "[{}]{}".format(time, user_name)

    # clean very old record from queue
    bad_record = []
    for existing_item in queue:
        try:
            record_unix_time = existing_item.split("]")[0].split("_")[1]
        except:
            continue

        #the checking include current user, if this user has a record too old, he/she should go to the back of the line.
        if EnneadTab.TIME.time_has_passed_too_long(record_unix_time):
            #default is 30mins
            bad_record.append(existing_item)
            #might make too old record removed later but not here,

    for bad in bad_record:
        queue.remove(bad)
        print ("Removing record that is older than 2 hours so it is not holding queue: {}".format(bad))


    # add to back of the list only if not registered before. Also only save the text if there is a change in queue
    for existing_item in queue:
        if user_name in existing_item:
            break
    else:
        queue.append(data)
        try:
            EA_UTILITY.save_list_to_txt(queue, log_file)
        except:
            # sh cannot write to L drive 
            return True
        

    if wait_num == 0 or user_name in queue[0] or envvars.get_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED"):

        # no one is on wait list now, should go ahead sync
        # or maybe username is at the begining of line, he can go sync as well.
        #or processing by sync all and close---> no dialogue wanted, but still write name to log
        return True


    current_queue = "Current Sync Queue:\n"
    quene_length = len(queue)
    for item in queue:
        current_queue += "\n  -" + item
    current_queue += "\n\nWhen There are no other people on the list, or you are the first on the wait list you can sync normally.\nRecord older than 30mins will be removed from the queue to avoid holding line too long."
    opts = [["I will join the waitlist and sync later.(Click 'Close' when you see Revit Sync Fail on next step, it just means the sync has been cancelled. You still hold position on the waitlist.)","Resume working and try syncing later.(+ $50 EA Coins)"], ["I don't care! Sync me now!","Jump in line will make other people who are syncing has to wait longer.(- $100 EA Coins for every position cut line)"]]
    res = EA_UTILITY.dialogue(main_text = "There are other people queuing before you, do you want to resume working and try sync later?\n\nYour name has been added to the wait list even if you cancel current sync.\n\n[You are also welcomed to save local while waiting.]",
                            sub_text = current_queue,
                            options = opts)
    if res == opts[1][0]:
        ENNEAD_LOG.sync_queue_cut_in_line(quene_length - 1)
        return True

    # if after all checking you are this step, that means you want to cancel now
    EXEC_PARAMS.event_args.Cancel()
    envvars.set_pyrevit_env_var("IS_SYNC_CANCELLED", True)
    ENNEAD_LOG.sync_queue_wait_in_line()


    try:
        doc.Save()
        EA_UTILITY.show_toast(title = "Your local file is saved.")

    except Exception as e:
        #print "file not saved"
        #print (e) #---->save doc is not allowed in this event
        pass
    return False





@EnneadTab.ERROR_HANDLE.try_pass
def fill_drafter_info():
    all_sheets = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Sheets).ToElements()
    free_sheets = EnneadTab.REVIT.REVIT_SELECTION.filter_elements_changable(all_sheets)
    
    t = DB.Transaction(doc, "Fill Drafter Info")
    t.Start()
    for sheet in free_sheets:
        sheet.LookupParameter("Drawn By").Set(DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, sheet.Id).Creator)
        
        sheet.LookupParameter("Designed By").Set(DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, sheet.Id).LastChangedBy)
    t.Commit()




@EnneadTab.ERROR_HANDLE.try_catch_error_silently
def main():


    if EnneadTab.ENVIRONMENT_CONSTANTS.is_Revit_limited():
        return

    if not EnneadTab.ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return

    VERSION_CONTROL.update_EA_dist()
    
    EnneadTab.LOG.update_time_sheet_revit(doc.Title)


    can_sync = check_sync_queue()
    if can_sync:
        ENNEAD_LOG.update_account_by_local_warning_diff(doc)



    # do this after checking ques so the primary EXE_PARAM is same as before
    fill_drafter_info()




    
    
    envvars.set_pyrevit_env_var("IS_DOC_CHANGE_HOOK_ENABLED", False)


#################################################################

output = script.get_output()
output.close_others()
output.self_destruct(50)




if __name__ == "__main__":



    main()