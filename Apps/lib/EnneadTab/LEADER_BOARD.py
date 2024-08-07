
import DATA_FILE
import FOLDER
import USER

from CONFIG import GLOBAL_SETTING_FILE

PRICE = {
    "daily_reward": {
        "money_delta":99,
        "description":"xxx"
        },
    "sync_queue_cut": {
        "money_delta":-500,
        "description":"xxx"
        },
    "sync_queue_stay": {
        "money_delta":200,
        "description":"xxx"
        },
}


@FOLDER.backup_data(GLOBAL_SETTING_FILE , "setting")
def update_account(event_key):
    event_data = PRICE.get(event_key)
    if not event_data:
        raise "Cannot find event key {}".format(event_key)
    with DATA_FILE.update_data(GLOBAL_SETTING_FILE) as data:
        
        if "money" not in data.keys():
            data["money"] = 100
        data["money"] += event_data.get("money_delta")
        return data["money"]
    
def get_money():
    return update_account(0)






def print_leader_board():
    pass

def print_history():
    pass

def manual_transaction():
    pass


def get_data_by_name():
    pass

def set_data_by_name():
    pass

def daily_reward():
    pass

def sync_queue_cut_in_line():
    pass

def sync_queue_wait_in_line():
    pass

def sync_gap_too_long():
    pass

def open_doc_with_warning_count():
    pass