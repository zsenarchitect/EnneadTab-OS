__doc__ = "Pick many families, and load them to many projects. You can:\n\t- 1 family >> x projects\n\t- x families >> 1 projects\n\t- x families >> x projects\n\t- 1 family >> 1 project\n\nHave bonus option to sync and close after done. And have option to pre-pick shared family loading behaviour. Handy for loading big family at end of day."
__title__ = "Load Multiple Families\nTo Multiple Docs"
__tip__ = True
from pyrevit import forms, DB, UI, script


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_FORMS, REVIT_APPLICATION
from EnneadTab import SOUND, ERROR_HANDLE

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


class FamilyOption(DB.IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        update_log( "#Normal Family Load option")
        update_log( "is family in use?: {}".format(familyInUse))
        overwriteParameterValues = True# true means use project value
        update_log( "is overwriteParameterValues?: {}".format(overwriteParameterValues))
        update_log( "should load")
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        update_log( "#Shared Family Load option")
        update_log( "is family in use?: {}".format(familyInUse))
        overwriteParameterValues = True
        update_log( "is overwriteParameterValues?: {}".format(overwriteParameterValues))

        global LOADING_SOURCE
        source = LOADING_SOURCE
        #source = DB.FamilySource.Family
        update_log( "is shared component using family or project definition?: {}".format(str(source)))
        update_log( "should load")
        return True

def load_family_to_docs(doc, family_doc):
    #t = DB.Transaction(doc, "Load family")
    #t.Start()
    if not family_doc:
        update_log("\n\n!! Cannot find family doc, contact SZ for debugging.")
        return
    try:
        update_log("\n\nLoading [{}]".format(family_doc.Title))
    except:
        update_log("\n\n!! Cannot get family, contact SZ for debugging.")
        return
    try:
        family_doc.LoadFamily(doc, FamilyOption())
        update_log("Family load succesfully to {}.".format(doc.Title))
    except Exception as e:
        update_log("Family [{}] fail to load to {}.\n Error = {}".format(family_doc.Title, doc.Title, e))
    #t.Commit()

    try:
        family_doc.Close(False)
    except:
        return
        """
        (To do)alternatively, it should open a safety doc before closing family doc.
        Revit API cannot close active doc with active view, so need to switch to other file first.
        """
        print("Cannot close {}".format(family_doc.Title))

def update_log(string):
    global LOG
    LOG.append(string)




def pick_open_family_docs():
    docs = EA_UTILITY.get_application().Documents
    OUT = []
    for doc in docs:
        if doc.IsFamilyDocument:
            OUT.append(doc)


    selected_family_docs = forms.SelectFromList.show(OUT,
                                            name_attr = "Title",
                                            multiselect = True,
                                            title = "pick families to load",
                                            button_name='pick families')
    
    return selected_family_docs


def pick_family_from_folder():
    source_files = forms.pick_file(file_ext = "rfa", multi_file = True)
    if not source_files:
        return None
    opened_docs = []
    for source_file in source_files:
        uidoc = UI.UIApplication(REVIT_APPLICATION.get_application()).OpenAndActivateDocument (source_file)
        opened_docs.append(uidoc.Document)
        
    return opened_docs


@ERROR_HANDLE.try_catch_error()
def process_family():

    

    open_docs = EA_UTILITY.get_top_revit_docs()
    selected_docs = forms.SelectFromList.show(open_docs,
                                            name_attr = "Title",
                                            multiselect = True,
                                            title = "Pick your destination documents",
                                            button_name='Load To Those Docs')

    options = [["Project Version",""], ["Family Doc Version","(Recommanded)"]]
    res = EA_UTILITY.dialogue(main_text = "When shared component is disovered, which version to use?", sub_text = "If there are no shared family, you can click on any option to processed.\n\nIf not sure, consault with your ACE first on how your project should treat shared family normally.", options = options)
    global LOADING_SOURCE
    if res == options[0][0]:
        LOADING_SOURCE = DB.FamilySource.Project
    else:
        LOADING_SOURCE = DB.FamilySource.Family

    global LOG
    LOG = []

    will_sync_and_close = EA_UTILITY.do_you_want_to_sync_and_close_after_done()



    opts = ["Pick From Opened Families", "Pick Families From A Folder."]
    res = REVIT_FORMS.dialogue(main_text = "Where to search for family?",
                                            options = opts)
    if res == opts[0]:
        selected_family_docs = pick_open_family_docs()
        # print selected_docs
    elif res == opts[1]:
        selected_family_docs = pick_family_from_folder()
        # print selected_docs
    
    
    if selected_family_docs is None:
        return
    
    
    
    
    for selected_family_doc in selected_family_docs:
        # action begin
        try:
            selected_family_doc.Save()
            update_log("family save success.")
        except Exception as e:
            update_log("fail to save family becasue: {}".format(e))
            #print "fail to save becasue: {}".format(e)


        for doc in selected_docs:
            load_family_to_docs(doc, selected_family_doc)


        EA_UTILITY.tool_has_ended()


        doc_list = ""
        for doc in selected_docs:
            doc_list += "\n" + doc.Title

        try:
            print(REVIT_FORMS.notification(main_text = "Family [{}] has been loaded to following docs:".format(selected_family_doc.Title), sub_text = doc_list, self_destruct = 3))
        except:
            pass
        #close_family(selected_family_doc)


    for line in LOG:
        print(line)

    if will_sync_and_close:
        REVIT_APPLICATION.sync_and_close()
    """
    options = ["Yes", "No"]
    res = EA_UTILITY.dialogue(main_text = "Loading finish, you want to close family doc?", options = options)
    if res == options[0]:
        try:

            selected_family_doc.Close()
        except Exception as e:
            print("Fail to close family doc becasue: {}".format(e))
    """



def close_family(family_doc):
    """ to do item: make a close family function after loading"""
    #Application
    all_docs = family_doc.Application.Documents
    uidoc.SaveAndClose()
    family_doc.Close(False)
    return
    ui_views = uidoc.GetOpenUIViews ()
    print(ui_views)
    print([x.viewid for x in ui_views])
    uidoc.RequestViewChange (my_view)
    uidoc.RefreshActiveView ()
    if will_close_family:
        uidoc.SaveAndClose()

def main():
    process_family()
    # action finished
    SOUND.play_sound("sound_effect_notification_position.wav")

################## main code below #####################

output = script.get_output()
output.close_others()

if __name__ == "__main__":
    main()
