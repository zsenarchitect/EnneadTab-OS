"""this is the module for finding secret token and api key
that should not be stored in any repo"""

import DATA_FILE, ENVIRONMENT

def get_api_key(app_name):
    file_path = "{}\\EA_API_KEY.secret".format(ENVIRONMENT.DB_FOLDER)
    data = DATA_FILE.get_data(file_path)
    return data.get(app_name)