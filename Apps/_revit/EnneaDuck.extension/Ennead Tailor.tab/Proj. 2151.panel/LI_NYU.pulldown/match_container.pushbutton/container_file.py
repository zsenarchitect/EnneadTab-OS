import System # pyright: ignore 
from pyrevit.revit import ErrorSwallower

from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_EVENT


from Autodesk.Revit import DB # pyright: ignore 
def open_container_file():
    container_file_title = "EAEC_NYU-Langone Health_Container File"
    for opened_doc in REVIT_APPLICATION.get_top_revit_docs():
        if opened_doc.Title == container_file_title:
            return opened_doc

    
    data = DATA_FILE.get_data("DOC_OPENER_DATA.sexyDuck", is_local=False)
    
    REVIT_EVENT.set_open_hook_depressed(True)
    warnings = ""
    with ErrorSwallower() as swallower:
        open_doc_siliently(container_file_title, data)
        errors = swallower.get_swallowed_errors()
        #print errors
        if len(errors) != 0:
            warnings += "\n\n{}".format(errors)
        
        
        model_path = tuple_to_model_path(data.get(container_file_title, None))
        if not model_path:
            NOTIFICATION.messenger("Cannot find the container file path, ask SZ for help.")
        REVIT_APPLICATION.open_and_active_project(model_path)


    REVIT_EVENT.set_open_hook_depressed(False)

    container_doc = [x for x in REVIT_APPLICATION.get_top_revit_docs() if x.Title == container_file_title][0]
    return container_doc

        
def tuple_to_model_path(tuple):
        if not tuple:
            return

        project_guid = tuple[0]
        file_guid = tuple[1]
        region = tuple[2]

        cloud_path = DB.ModelPathUtils.ConvertCloudGUIDsToCloudPath(region, System.Guid(project_guid), System.Guid(file_guid))
        return cloud_path

def open_doc_siliently(doc_name, data):
    if doc_name not in data:
        print ("[{}] has not been recorded by EnneadTab before in data".format(doc_name))
        return
    
    
    cloud_path = tuple_to_model_path(data[doc_name])

    open_options = DB.OpenOptions()
    open_options.SetOpenWorksetsConfiguration (DB.WorksetConfiguration(DB.WorksetConfigurationOption.CloseAllWorksets ) )

    try:
        # __revit__.OpenAndActivateDocument (cloud_path, open_options, False) # pyright: ignore 
        
        new_doc = REVIT_APPLICATION.get_app().OpenDocumentFile(cloud_path,
                                                                open_options)
        return
    except Exception as e:
        return
        print ("{} cannot be opened becasue {}".format(doc_name, e))