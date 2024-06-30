
import DATA_FILE
import FOLDER
import USER

RECORD_FILE = FOLDER.get_EA_dump_folder_file('personal_record_{}.json'.format(USER.USER_NAME))

@FOLDER.backup_data(RECORD_FILE , "personal_record")
def update_money(coin_change):
    with DATA_FILE.update_data(RECORD_FILE) as data:
        if "money" not in data.keys():
            data["money"] = 100
        data["money"] += coin_change
        return data["money"]
    
def get_money():
    return update_money(0)

