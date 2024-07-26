"""used to retrive sample file in rhino, reivt and excel.
Good the sharing template"""

import os
import ENVIRONMENT
import NOTIFICATION

def get_file(file_name):
        
    path = "{}\\{}\\{}".format(ENVIRONMENT.DOCUMENT_FOLDER, ENVIRONMENT.get_app_name(), file_name)
    if os.path.exists(path):
        return path
    NOTIFICATION.messenger("Cannot find [{}]".format(file_name))