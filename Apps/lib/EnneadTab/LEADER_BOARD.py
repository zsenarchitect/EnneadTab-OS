
import DATA_FILE
import FOLDER
import USER

from CONFIG import SETTING_FILE_NAME

@FOLDER.backup_data(SETTING_FILE_NAME , "setting")
def update_money(coin_change):
    with DATA_FILE.update_data(SETTING_FILE_NAME) as data:
        
        if "money" not in data.keys():
            data["money"] = 100
        data["money"] += coin_change
        return data["money"]
    
def get_money():
    return update_money(0)

