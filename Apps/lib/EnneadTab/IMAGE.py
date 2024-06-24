import os
import ENVIRONMENT

def get_image_path_by_name(file_name):
    if os.path.exists("{}\\{}".format(ENVIRONMENT.IMAGE_FOLDER, file_name)):
        return "{}\\{}".format(ENVIRONMENT.IMAGE_FOLDER, file_name)
    print ("A ha! {}\\{} is not valid or accessibile. Better luck next time.".format(ENVIRONMENT.IMAGE_FOLDER, file_name))
