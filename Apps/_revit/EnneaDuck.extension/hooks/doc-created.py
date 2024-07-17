
from pyrevit import EXEC_PARAMS
from pyrevit.coreutils import envvars
import EnneadTab



def proj_initiation():
    if EnneadTab.ENVIRONMENT.is_RhinoInsideRevit_environment():
        return

    
    try:
        doc = EXEC_PARAMS.event_args.Document
    except:
        return


    if doc is None:
        return

    if doc.IsFamilyDocument:
        return
    
    
    # testers = ["scott.mackenzie",
    #             "achi",
    #             "gayatri.desai",
    #             "szhang",
    #             "laren.sakota"]
    # if not EnneadTab.USER.get_user_name() in testers:
    #     return
    
    # EnneadTab.NOTIFICATION.duck_pop(main_text = "Tester to event hook to new document creation.")
    # print ("Tester to event hook to new document creation.")
    # print ("Other testers are:")
    # for name in testers:
        
    #     print (name)
        
    import imp
    folder = r"C:\Users\szhang\github\EnneadTab-for-Revit\ENNEAD.extension\Ennead.tab\ACE.panel\Project Starter.pushbutton"
    func_name = "project_starter"
    full_file_path = r"{}\{}_script.py".format(folder, func_name)
    if not  EnneadTab.USER.is_SZ():
        full_file_path =  EnneadTab.FOLDER.remap_filepath_to_folder(full_file_path)
        
    ref_module = imp.load_source("{}_script".format(func_name), full_file_path)


    getattr(ref_module, func_name)(doc)
    
    
    
if __name__ == "__main__":
    proj_initiation()