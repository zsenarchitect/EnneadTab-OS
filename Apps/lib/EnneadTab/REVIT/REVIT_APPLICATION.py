#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from Autodesk.Revit import UI # pyright: ignore
    from Autodesk.Revit import DB # pyright: ignore
    import REVIT_FORMS, REVIT_EVENT
except:
    pass


import FOLDER, SAMPLE_FILE


def get_app():
    app = __revit__ # pyright: ignore
    if hasattr(app, 'Application'):
        app = app.Application
    return app


def get_uiapp():
    """Return UIApplication provided to the running command."""
    if isinstance(__revit__, UI.UIApplication): # pyright: ignore
        return __revit__  # pyright: ignore

    from Autodesk.Revit import ApplicationServices # pyright: ignore
    if isinstance(__revit__, ApplicationServices.Application): # pyright: ignore
        return UI.UIApplication(__revit__) # pyright: ignore
    return __revit__ # pyright: ignore


def get_uidoc():
    """Return active UIDocument."""
    return getattr(get_uiapp(), 'ActiveUIDocument', None)


def get_doc():
    """Return active Document."""
    return getattr(get_uidoc(), 'Document', None)



def get_active_view():
    """Return view that is active (UIDocument.ActiveView)."""
    return getattr(get_uidoc(), 'ActiveView', None)


def do_you_want_to_sync_and_close_after_done():
    will_sync_and_close = False
    res = REVIT_FORMS.dialogue(main_text = "Sync and Close after done?", options = ["Yes", "No"])
    if res == "Yes":
        will_sync_and_close = True

    return will_sync_and_close



def sync_and_close(close_others = True, disable_sync_queue = True):

    from pyrevit import script
    from pyrevit.coreutils import envvars
    output = script.get_output()
    killtime = 30
    output.self_destruct(killtime)

    import REVIT_VIEW
    REVIT_EVENT.set_sync_queue_enable_stage(disable_sync_queue)
    if close_others:
        envvars.set_pyrevit_env_var("IS_AFTER_SYNC_WARNING_DISABLED", True)
        # if you descide to close others, they should be no further warning. Only recover that warning behavir in DOC OPENED event


    def get_docs():
        try:
            doc = __revit__.ActiveUIDocument.Document # pyright: ignore
            docs = doc.Application.Documents
            print("get docs using using method 1")
        except:
            docs = __revit__.Documents #pyright: ignore
            print("get docs using using method 2")
        print( "Get all docs, inlcuding links and family doc = {}".format(str([x.Title for x in docs])))
        return docs

    print("getting docs before sync")
    docs = get_docs()
    logs = []

    for doc in docs:

        if doc.IsLinked or doc.IsFamilyDocument:
            continue
        REVIT_VIEW.switch_to_sync_draft_view(doc)
        # print "#####"
        # print ("# {}".format( doc.Title) )
        #with revit.Transaction("Sync {}".format(doc.Title)):
        t_opts = DB.TransactWithCentralOptions()
        #t_opts.SetLockCallback(SynchLockCallBack())
        s_opts = DB.SynchronizeWithCentralOptions()
        s_opts.SetRelinquishOptions(DB.RelinquishOptions(True))

        s_opts.SaveLocalAfter = True
        s_opts.SaveLocalBefore = True
        s_opts.Comment = "EnneadTab Batch Sync"
        s_opts.Compact = True


        try:
            doc.SynchronizeWithCentral(t_opts,s_opts)
            logs.append( "\tSync [{}] Success.".format(doc.Title))
            import SPEAK
            SPEAK.speak("Document {} has finished syncing.".format(doc.Title))
        except Exception as e:
            logs.append( "\tSync [{}] Failed.\n{}\t".format(doc.Title, e))

        REVIT_VIEW.switch_from_sync_draft_view()
    
    envvars.set_pyrevit_env_var("IS_SYNC_QUEUE_DISABLED", not(disable_sync_queue))
    for log in logs:
        print( log)
    if not close_others:
        return

    print("getting docs before active safty doc")
    docs = get_docs()
    open_safety_doc_family()
    print("active doc set as safety doc")
    for doc in docs:
        if doc is None:
            print("doc is None, skip")
            continue
        try:
            if doc.IsLinked:
                print("doc {} is a link doc, skip".format(doc.Title))
                continue
        except Exception as e:
            print ("Sync&Close Info:")
            print (e)
            print(str(doc))
            continue

        title = doc.Title
        try:
            print ("Trying to close [{}]".format(title))
            doc.Close(False)
            doc.Dispose()
        except Exception as e:
            print (e)
            try:
                print ("skip closing [{}]".format(title))
            except:
                print ("skip closing some doc")
        """
        try to open a dummy family rvt file in the buldle folder and switch to that as active doc then close original active doc
        """


def open_safety_doc_family():
    filepath = SAMPLE_FILE.get_file("EnneadTab Safety Doc.rfa")
    safe_family = FOLDER.copy_file_to_local_dump_folder(filepath, ignore_warning=True)

    open_and_active_project(safe_family)


def open_and_active_project(filepath):
    """return a ui document"""
    try:
        app = __revit__ #pyright: ignore
        return UI.UIApplication(app).OpenAndActivateDocument (filepath)
    except:
        pass

    try:
        app = __revit__.ActiveUIDocument.Document  #pyright: ignore
        return UI.UIApplication(app).OpenAndActivateDocument (filepath)
    except:
        pass

    try:
        app = __revit__.ActiveUIDocument.Document  #pyright: ignore
        open_options = DB.OpenOptions()
        return UI.UIApplication(app).OpenAndActivateDocument (filepath, open_options, False)
    except:
        pass

    try:
        app = __revit__ #pyright: ignore
        open_options = DB.OpenOptions()
        return UI.UIApplication(app).OpenAndActivateDocument (filepath, open_options, False)
    except:
        pass

    print ("Activate Failed")


def close_docs_by_name(names = [], close_all = False):
    """close opened docs by providing the name of the docs to close

    Args:
        names (list, optional): list of docs to close. Defaults to [].
        close_all (bool, optional): if true, close every open docs, you do not need to provide the name list. Defaults to False.
    """

    def safe_close(doc):
        name = doc.Title
        doc.Close(False)
        doc.Dispose()#########################
        print ("{} closed".format(name))

    docs = get_top_revit_docs()
    if close_all:
        map(safe_close, docs)
        return

    for doc in docs:
        if doc.Title in names:
            try:
                safe_close(doc)
            except Exception as e:
                print( e)
                print ("skip closing [{}]".format(doc.Title))


def get_top_revit_docs():
    """get main docs that is NOT link doc or family doc

    Returns:
        list of docs: all docs that is not link or family doc
    """


    docs = get_app().Documents
    OUT = []
    for doc in docs:
        if doc.IsLinked:
            continue
        if doc.IsFamilyDocument:
            continue
        OUT.append(doc)
    return OUT


def get_all_family_docs(including_current_doc = False):
    """get all the opened family docs

    Args:
        including_current_doc (bool, optional): if true, current family doc is included as well. Defaults to False.

    Returns:
        list of family docs: _description_
    """
    docs = get_app().Documents
    OUT = []
    for doc in docs:
        if not doc.IsFamilyDocument:
            continue
        if not including_current_doc:
            if doc.Title == __revit__.ActiveUIDocument.Document.Title: # pyright: ignore
                continue
        OUT.append(doc)
    return OUT


def select_family_docs(select_multiple = True, including_current_doc = False):
    """pick opended family docs.

    Args:
        select_multiple (bool, optional): _description_. Defaults to True.
        including_current_doc (bool, optional): _description_. Defaults to False.

    Returns:
        list of family docs: _description_
    """
    from pyrevit import forms
    title = "Pick Families" if select_multiple else "Pick Family"
    return forms.SelectFromList.show(get_all_family_docs(including_current_doc = including_current_doc),
                                        name_attr = "Title",
                                        multiselect = select_multiple,
                                        title = title,
                                        button_name=title)


def select_top_level_docs(select_multiple = True):
    from pyrevit import forms
    docs = get_top_revit_docs()
    docs = forms.SelectFromList.show(docs,
                                    name_attr = "Title",
                                    multiselect = select_multiple,
                                    title = "Pick some open revit docs")
    return docs






def get_revit_link_docs(including_current_doc = False, link_only = False):

    docs = get_app().Documents

    OUT = []
    for doc in docs:
        if doc.IsFamilyDocument:
            continue
        if not including_current_doc:

            try:
                if doc.Title == __revit__.ActiveUIDocument.Document.Title: # pyright: ignore
                    continue
            except:
                pass
        
        if link_only:
            if not doc.IsLinked:
                continue

        OUT.append(doc)
    OUT.sort(key = lambda x: x.Title)
    return OUT

def select_revit_link_docs(select_multiple = True, including_current_doc = False, link_only = False):
    from pyrevit import forms
    docs = get_revit_link_docs(including_current_doc = including_current_doc, link_only = link_only )
    docs = forms.SelectFromList.show(docs,
                                    name_attr = "Title",
                                    multiselect = select_multiple,
                                    title = "Pick some revit links")
    return docs




def close_revit_app():
    """try its best to close the revit session.
    """
    from Autodesk.Revit.UI import RevitCommandId,PostableCommand  #pyright: ignore

    uiapp = get_uiapp()


    CmndID = RevitCommandId.LookupPostableCommandId (PostableCommand .ExitRevit)
    CmId = CmndID.Id
    uiapp.PostCommand(CmndID)


