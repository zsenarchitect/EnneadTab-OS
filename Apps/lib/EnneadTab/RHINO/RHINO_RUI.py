import ENVIRONMENT
import FOLDER


if ENVIRONMENT.is_Rhino_environment():
    import rhinoscriptsyntax as rs


def update_my_rui():

    rs.CloseToolbarCollection("EnneadTab_For_Rhino_Installer", prompt=False)
    my_local_version = FOLDER.copy_file_to_local_dump_folder(ENVIRONMENT.RHINO_FOLDER + "\\EnneadTab_For_Rhino.rui")

    # close current toolbar so not holding it.
    rs.CloseToolbarCollection("EnneadTab_For_Rhino", prompt=False)
    rs.OpenToolbarCollection(my_local_version)


  
    
def unit_test():
    pass

    
if __name__ == "__main__":

    update_my_rui()