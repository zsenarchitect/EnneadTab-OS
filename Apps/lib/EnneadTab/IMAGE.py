import os
import random
import ENVIRONMENT


def get_image_path_by_name(file_name):
    if os.path.exists("{}\\{}".format(ENVIRONMENT.IMAGE_FOLDER, file_name)):
        return "{}\\{}".format(ENVIRONMENT.IMAGE_FOLDER, file_name)
    print ("A ha! {}\\{} is not valid or accessibile. Better luck next time.".format(ENVIRONMENT.IMAGE_FOLDER, file_name))



def get_one_image_path_by_prefix(prefix):
    files = [os.path.join(ENVIRONMENT.IMAGE_FOLDER, f) for f in os.listdir(ENVIRONMENT.IMAGE_FOLDER) if f.startswith(prefix)]
    file = random.choice(files)
    return file
