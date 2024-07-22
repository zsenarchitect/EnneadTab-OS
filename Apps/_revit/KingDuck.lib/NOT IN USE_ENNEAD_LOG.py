"""user name refer to the window ID name"""

import time
import os
import traceback
from EnneadTab import EMAIL, DATA_FILE, USER, FOLDER, SPEAK, NOTIFICATION, TIME, ENVIRONMENT, ENVIRONMENT
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FORMS


def try_catch_error(func):
    def wrapper(*args, **kwargs):
        """
        if not EA_UTILITY.is_SZ(pop_toast = False, additional_tester_ID = ["paula.gronda", "pnorcrossPYDAS", "laura.rodriguezEHAYS"]):#
            return False
        """

        # EA_UTILITY.print_note ("Wrapper func for EA Log -- Begin:")
        try:
            # print "main in wrapper"
            out = func(*args, **kwargs)
            # EA_UTILITY.print_note ( "Wrapper func for EA Log -- Finish:")
            return out
        except Exception as e:
            EA_UTILITY.print_note(str(e))
            EA_UTILITY.print_note(
                "Wrapper func for EA Log -- Error: " + str(e))
            update_error_log(traceback.format_exc())
            try:
                data_file = "{}\{}.sexyDuck".format(get_user_root_folder(), get_current_user_name())
                EMAIL.email(receiver_email_list=["szhang@ennead.com"],
                                      subject="EnneadTab Auto Email: EnneadLog feels sick",
                                      body=traceback.format_exc(),
                                      attachment_list = [data_file])
                
            except Exception as e:
                EMAIL.email(receiver_email_list=["szhang@ennead.com"],
                                      subject="EnneadTab Auto Email: EnneadLog feels sick",
                                      body=traceback.format_exc())
            return
    return wrapper


def create_user_data(name):
    data = dict()
    data["name"] = name
    data["money"] = 500
    data["history"] = ["User profile created"]
    data["time_stamp"] = [time.time()]
    data["Autodesk_ID"] = USER.get_autodesk_user_name()
    data["recent_projects"] = []
    file = "{}\{}.sexyDuck".format(get_user_root_folder(), name)
    # try:
    DATA_FILE.set_data(data, file)
    return data

    # except:
    #     # For SH people they cannot create any valid file, so this is a temproty solution

@try_catch_error
def force_clear_user(target_user_names = []):
    if target_user_names == []:
        return
    if get_current_user_name() in target_user_names:
        clear_user_data()
        
        
def clear_user_data():
    
    file = "{}\{}.sexyDuck".format(get_user_root_folder(), get_current_user_name())
    # try:
    if FOLDER.is_path_exist(file):
        os.remove(file)
        
        
def get_all_user_datas():
    datas = [get_data_by_name(x) for x in get_all_user_names()]
    return datas


def get_user_name_from_meta_file(file):
    name = FOLDER.get_file_name_from_path(file).split(".sexyDuck")[0]
    return name


def get_all_user_names():
    names = [get_user_name_from_meta_file(file)
             for file in get_all_user_meta_files()]
    try:
        names.remove("Error_Log")

    except Exception as e:
        pass
        # print str(e)
    return names


def get_all_user_meta_files():
    folder = get_user_root_folder()
    if not os.path.exists(folder):
        return []
    file_names = FOLDER.get_filenames_in_folder(folder)
    if "Error_Log.sexyDuck" in file_names:
        file_names.remove("Error_Log.sexyDuck")

    if "SH_tester_account.sexyDuck" in file_names:
        file_names.remove("SH_tester_account.sexyDuck")
    # print (file_names)
    return file_names


def get_user_data_file_by_name(user_name, level=0):
    for file in get_all_user_meta_files():
        if get_user_name_from_meta_file(file) == user_name:
            return file

    basic_data = create_user_data(user_name)

    print("New User File Created for " + user_name)
    if level == 0:

        return get_user_data_file_by_name(user_name, level=1)
    return basic_data


def get_current_user_name():
    import os
    user_name = os.environ["USERPROFILE"].split("\\")[-1]
    return user_name


def get_absolute_path(file_name):
    return "{}\{}".format(get_user_root_folder(), file_name)


def get_data_by_name(user_name=get_current_user_name()):
    file_name = get_user_data_file_by_name(user_name)
    data = DATA_FILE.read_json_as_dict(get_absolute_path(file_name))

    # uncomment below to find out which file has format issue in json
    # print "\n"
    # print user_name
    return data


def set_data_by_name(user_name, data):
    file_name = get_user_data_file_by_name(user_name)
    DATA_FILE.set_data(
        data, get_absolute_path(file_name), use_encode=True)


def get_value_or_default_value(dict, key, default):
    if key not in dict.keys():
        dict[key] = default
    return dict, dict[key]


def update_account(user_name=get_current_user_name(), coins_added=0, history_added=None, doc=None):
    data = get_data_by_name(user_name)
    if not data:
        if get_current_user_name() == "szhang":
            print (user_name + " no good data")
            os.startfile(get_user_data_file_by_name(user_name))
        return
    data["money"] += coins_added

    if not data.has_key("time_stamp") or not data.has_key("history"):
        create_user_data(user_name)
        return

    current_doc_name = get_central_name(doc)
    # print current_doc_name
    data, value = get_value_or_default_value(
        data, "recent_projects", [current_doc_name])
    if current_doc_name not in data["recent_projects"]:
        data["recent_projects"].append(current_doc_name)

    data["history"].append(history_added)
    data["time_stamp"].append(time.time())
    data["is_TTS_killed"] = is_TTS_killed()
    set_data_by_name(user_name, data)


def update_history(user_name=get_current_user_name(), history_added=None):
    data = get_data_by_name(user_name)
    if not data:
        if get_current_user_name() == "szhang":
            print (user_name + " no good data")
            os.startfile(get_user_data_file_by_name(user_name))
        return
    if "history" not in data.keys() or "time_stamp" not in data.keys():
        create_user_data(user_name)
        return
    data["history"].append(history_added)
    data["time_stamp"].append(time.time())
    set_data_by_name(user_name, data)


@try_catch_error
def update_local_warning(doc):
    central_name = get_central_name(doc)
    if central_name == "Zero Doc":
        return

    user_name = get_current_user_name()

    data = get_data_by_name(user_name)
    if not data:
        return

    keyA = "local_warning"
    if not data.has_key(keyA):
        data[keyA] = dict()

    data[keyA][central_name] = len(list(doc.GetWarnings()))

    keyB = "local_warning_dict"
    if not data.has_key(keyB):
        data[keyB] = dict()

    data[keyB][central_name] = get_current_warning_dict(doc)

    set_data_by_name(user_name, data)
    # EA_UTILITY.show_toast(title = "Current warning = {}".format(len(list(doc.GetWarnings()))))


@try_catch_error
def get_local_warning_difference(doc):
    # larger than 0 means increase
    # smaller than 0 means decrease
    user_name = get_current_user_name()
    data = get_data_by_name(user_name)
    if not data:
        return 0
    if not data.has_key("local_warning"):
        return 0

    central_name = get_central_name(doc)
    if central_name == "Zero Doc":
        return 0
    current_warning = len(list(doc.GetWarnings()))
    if central_name not in data["local_warning"].keys():
        return 0
    record_warning = data["local_warning"][central_name]
    return current_warning - record_warning


@try_catch_error
def get_local_warning_dict_difference(doc):
    """ compare what is new warning introduced this session , return a list of text that says how many X warning is introduced."""

    user_name = get_current_user_name()
    data = get_data_by_name(user_name)
    if not data.has_key("local_warning_dict"):
        return []

    central_name = get_central_name(doc)
    if central_name == "Zero Doc":
        return []
    current_warning_dict = get_current_warning_dict(doc)
    if central_name not in data["local_warning_dict"].keys():
        return []

    OUT = []
    record_warning_dict = data["local_warning_dict"][central_name]
    for description in current_warning_dict.keys():
        if description not in record_warning_dict.keys():
            record_warning_dict[description] = 0
        diff = current_warning_dict[description] - \
            record_warning_dict[description]
        print(description)
        if diff > 0:
            OUT.append("--[{}]: +{} warnings.".format(description, diff))
        elif diff < 0:
            OUT.append("--[{}]: -{} warnings.".format(description, -diff))
        else:
            pass
    return OUT


@try_catch_error
def get_current_warning_dict(doc):
    warning_dict = dict()
    for warning in doc.GetWarnings():
        description = warning.GetDescriptionText()
        if description not in warning_dict.keys():
            warning_dict[description] = 1
        else:
            warning_dict[description] += 1

    return warning_dict


@try_catch_error
def update_account_by_local_warning_diff(doc):
    """
    if get_current_user_name() in  ["gayatri.desai"]:

        return
    """

    local_diff = get_local_warning_difference(doc)
    if local_diff == 0 or local_diff is None:
        return

    if local_diff > 0:
        tool_used = "In Session Creating Warning."
        price = 1
    else:
        tool_used = "In Session Reducing Warning."
        price = 2

    # if increase warning, reduce coins---> always opposite
    coin_change = - int(local_diff * price)

    additional_note = ""
    is_sending_log = get_current_user_name() in ["paula.gronda"]
    if abs(local_diff) > 10 and is_sending_log:
        local_warning_diff_list = get_local_warning_dict_difference(doc)
        if len(local_warning_diff_list) > 0:

            additional_note += "\n".join(local_warning_diff_list)
            EMAIL.email(receiver_email_list=["szhang@ennead.com", "{}@ennead.com".format(get_current_user_name())],
                                  subject="EnneadTab Auto Email: Warning Change Log",
                                  body="Q: What is this email?\nA: This is a warning change log for your record.\n\nUser: {}\nProject File: {}\nWarning Change Since Last Record:{}\n\n\n\n{}".format(get_current_user_name(),
                                                                                                                                                                                                      get_central_name(
                                                                                                                                                                                                          doc),
                                                                                                                                                                                                      local_diff,
                                                                                                                                                                                                      additional_note))

    # print additional_note

    if abs(coin_change) > 2500 and DATA_FILE.get_revit_ui_setting_data(("checkbox_email_local_warning_diff", True)):
        SPEAK.speak(
            "hmm.. Something is fishy here. How did you have a change of {} coins? Let me write an email. Hold my beer.".format(coin_change))
        EMAIL.email(receiver_email_list=["szhang@ennead.com", "{}@ennead.com".format(get_current_user_name())],
                              subject="EnneadTab Auto Email: Local warning too Many Coins change!",
                              body="Q: What is this email?\nA: This means the YOU have introduced or removed warnings for the project in YOUR session.\n\nQ: How does it know it is me not others?\nA: The record looks for the warnings at the openning of the file, and compare it to the number of warnings when you are about to sync. The difference of the two are all warnings added or removed by you in this session. After the sync, warnings from other people might come in, so the record is reset to that status, and wait to be compared before your next sync.\n\nUser: {}\nProject File: {}\nWarning Change Since Last Record:{}\nUnit Price:{}\nCoin Change:{} {}".format(get_current_user_name(),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            get_central_name(
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                doc),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            local_diff,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            price,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            coin_change,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            additional_note))
        return
    else:
        update_account(coins_added=coin_change,
                       history_added=tool_used, doc=doc)

    """
    if not EA_UTILITY,IS_DEVELOPER:
        return
    """

    if local_diff > 0:
        log_money_change_toast(title="In Session {} Warnings Created By You: Pay {} EA Coins".format(abs(local_diff), abs(coin_change)),
                               message="Every new warning will cost you {} coins.".format(
                                   price),
                               gain_money=False)

        lines = ["Warnings, warning, they are everywhere...",
                 "When is the last time you cleaned your revit warning? Two olympics ago?",
                 "There is no shame in getting more warning than before, I repeat, no shame, shame , shame, shame. Did you hear echo?",
                 "Knock knock. Who is there? {} warnings".format(local_diff),
                 "{} warnings walks into a bar...".format(local_diff)]
        SPEAK.random_speak(lines)

    else:
        log_money_change_toast(title="In Session {} Warnings Resolved By You: Gain {} EA Coins.".format(abs(local_diff), abs(coin_change)),
                               message="Rewarded {} coins per warning reduced.".format(
                                   price),
                               gain_money=True)

        lines = ["A clean revit is a happy revit.",
                 "It is always nice to see less warning.",
                 "Let's go! Keep the warning down!"]
        SPEAK.random_speak(lines)


def is_TTS_killed():
    return not DATA_FILE.get_revit_ui_setting_data(("toggle_bt_is_talkie", True))
    """
    dump_folder = EA_UTILITY.get_EA_local_dump_folder()
    file_name = "EA_TALKIE_KILL.kill"

    if EA_UTILITY.is_file_exist_in_folder(file_name, dump_folder):
        return True
    return False
    """


def get_central_name(doc=None):
    if not doc:
        try:
            doc = REVIT_APPLICATION.get_doc()
        except Exception as e:
            print("Default doc getter error")
            print(traceback.format_exc())
            doc = __revit__.ActiveUIDocument.Document # pyright: ignore

    if not doc:
        return "Zero Doc"
    if not hasattr(doc, "Title"):
        return "Zero Doc"

    try:
        return doc.Title.replace("_{}".format(USER.get_autodesk_user_name()), "")
    except Exception as e:
        # print str(e)
        # print "LOG get central name error"
        EMAIL.email(receiver_email_list=["szhang@ennead.com"],
                              subject="EnneadTab Auto Email: Title error",
                              body=traceback.format_exc())
        try:
            return doc.Title
        except:

            return "Zero Doc"


def get_user_root_folder():
    """ wait for the new home in AVD"""
    if not ENVIRONMENT.IS_L_DRIVE_ACCESSIBLE:
        return NOTIFICATION.DUMP_FOLDER
    
    folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Users"
    folder = FOLDER.secure_folder(folder)
    try:
        res = DATA_FILE.set_data(
            dict(), folder + "\\SH_tester_account.sexyDuck")
        if not res:
            folder = NOTIFICATION.DUMP_FOLDER
    except:
        folder = NOTIFICATION.DUMP_FOLDER
    finally:
        return folder


@try_catch_error
def is_money_negative(user_name=get_current_user_name()):

    if get_current_money(user_name) <= 0:

        # dont alert too often for bankrupt
        if is_recently_recorded(tool_used="Bankrupt", search_length=10):
            return False

        SPEAK.speak(
            "You are bankrupt. Don't worry, you are not the only one.")
        folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc"
        image = "LOG_BANKRUPT.png"

        NOTIFICATION.messenger(main_text="Woahaha! You don't have enough EA Coins...",
                                     sub_text="Current Balance = {} EA Coins".format(
                                         get_current_money()),
                                     icon="{}\{}".format(folder, image),
                                     app_name="EnneadTab Mini Bank",
                                     importance_level=0)

        update_history(user_name, history_added="Bankrupt")

        return True
    return False


@try_catch_error
def get_current_money(user_name=get_current_user_name()):
    data = get_data_by_name(user_name)
    if not data:
        
        return 0

    return data.get("money", 0)


def log_money_change_toast(title, message, gain_money=True):

    folder = r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc"
    if gain_money:
        image = "LOG_TOAST_MONEY_GAIN.png"
    else:
        image = "LOG_TOAST_MONEY_LOST.png"

    NOTIFICATION.messenger(main_text=title,
                                 sub_text=message,
                                 icon="{}\{}".format(folder, image),
                                 app_name="Current Balance = ${} @EnneadTab Mini Bank".format(
                                     get_current_money()),
                                 importance_level=0)


"""action for the record"""


def print_leader_board():

    from pyrevit import script
    output = script.get_output()
    output.close_others()
    output.center()
    output.set_title("Congratulation!!")
    # print "Leaderboard"
    datas = get_all_user_datas()
    # return
    # print (datas[0:2])
    datas = filter(lambda x: x is not None and x.has_key("money"), datas)
    datas.sort(key=lambda x: x["money"], reverse=True)
    datas.sort(key=lambda x: x["name"] == "szhang")

    """
        bold ====   **text**
        italic ====   *text*
        bold and italic ======   ***text***
        heading =======   ## text   (# biggest, ##### smallest)
    """
    output.print_md("##EnneadTab Mini Bank Leader Board:##")
    for i, data in enumerate(datas):
        if data["name"] == "paula.gronda":
            add_additional_icon = ":crown:"

        elif data["name"] == "jihyeon.park":
            add_additional_icon = ":fox_face:"
        else:
            add_additional_icon = ""

        if data.has_key("is_TTS_killed"):
            if data["is_TTS_killed"]:
                add_additional_icon += " :zipper-mouth_face:"

        if i < 3:
            output.print_md("<***{}***> :money_bag: : **{}** {}: **${}** ".format(
                i + 1, data["name"], add_additional_icon, data["money"]))
        else:
            if data["name"] != "szhang":
                output.print_md("{}: {} {}: **${}**".format(i + 1,
                                data["name"], add_additional_icon, data["money"]))

            else:
                output.print_md("{}: {} {}: ${}".format(
                    "-" * len(str(i+1)), data["name"], add_additional_icon, data["money"]))

    print("Congratulation to everyone!")
    print("Note: If you are wondering about the zipper mouth icon, those people has decided to mute the talkie lady.")

    output.print_image(
        r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Misc\Rich_Duck.jpg")


def assign_default_key_values_to_data(data):
    checker_list = [("history", "User profile created"),
                    ("time_stamp", time.time()),
                    ("recent_projects", None)]
    is_valid = True
    for checker_key, default_value in checker_list:
        if checker_key not in data.keys():
            if default_value is None:
                data[checker_key] = []
            else:
                # make sure it is starting a list
                data[checker_key] = [default_value]

            is_valid = False

    if not is_valid:
        user = data["name"]
        # print user
        set_data_by_name(user, data)
    return data


def manual_transaction():
    from pyrevit import forms

    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "{} <{}>".format(self.item, get_data_by_name(self.item)["money"])

    while True:
        opts = [MyOption(x) for x in get_all_user_names()]
        opts.insert(0, "--Quit--")
        selected_name = forms.SelectFromList.show(opts,
                                                  multiselect=False,
                                                  title="Pick user names to check their history.")
        if not selected_name:
            return
        if "quit" in selected_name.lower():
            return

        data = get_data_by_name(selected_name)
        current_money = data["money"]
        change = forms.ask_for_string(
            prompt="User {} current money is {}. Use +- for gain/reduce".format(selected_name, current_money))
        try:
            data["money"] += int(change)
            set_data_by_name(selected_name, data)
            update_history(user_name=selected_name,
                           history_added="Financial Aids ${}".format(int(change)))
        except Exception as e:
            print(e)


def print_history(user_lookup=None):

    from pyrevit import forms
    selected_names = forms.SelectFromList.show(get_all_user_names(),
                                               multiselect=True,
                                               title="Pick user names to check their history.")
    if not selected_names:
        return

    for user in selected_names:
        data = get_data_by_name(user)
        data = assign_default_key_values_to_data(data)
        print("\n\n##################")
        print("Checking records for : " + user)
        print("Current Mini Bank Balance = ${}".format(data["money"]))
        if len(data["recent_projects"]) > 0:
            print("Recently working on files:")
            for project in data["recent_projects"]:
                print("\t{}".format(project))
        # print data
        for time_stamp, history in zip(data["time_stamp"], data["history"]):

            t = time.strftime("%Y-%m-%d %H:%M:%S",
                              time.localtime(int(time_stamp)))

            print("{} : {}".format(t, history))


def print_error_log(user_lookup=None):
    # from datetime import datetime
    data = get_data_from_error_log()

    from pyrevit import forms
    selected_names = forms.SelectFromList.show(data.keys(),
                                               multiselect=True,
                                               title="Pick user names who had error report.")
    if not selected_names:
        return

    for user, user_record in data.items():
        if user not in selected_names:
            continue
        print("\n\n##################")
        print("Checking records for : " + user)
        for report in user_record:  # user_record is a list
            print("\n--------------------------------")
            print("User = " + user)
            for key, value in report.items():
                print("\n\n")

                print("Report Key = {}".format(key))

                if str(key) == "error_time":
                    value = time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(int(value)))

                    """
                    ts = int(value)
                    # if you encounter a "year is out of range" error the timestamp
                    # may be in milliseconds, try `ts /= 1000` in that case
                    value = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    """

                print("Report Value = {}".format(value))


def update_error_log(error, user_name=get_current_user_name()):
    data = get_data_from_error_log()

    if not data.has_key(user_name):
        data[user_name] = []
    report = dict()
    report["error"] = str(error)
    report["error_time"] = time.time()
    data[user_name].append(report)
    set_data_to_error_loge(data)


def get_data_from_error_log():
    data = DATA_FILE.read_json_as_dict(
        r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Users\Error_Log.sexyDuck")
    return data


def set_data_to_error_loge(data):
    DATA_FILE.set_data(
        data, r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Project Settings\Users\Error_Log.sexyDuck")


def is_recently_recorded(tool_used, search_length=5):
    """get record to see, if in the last several record the 'tool_used' is NOT there, then it worth recroding."""
    data = get_data_by_name()
    if not data:
        return False
    if not data.has_key("time_stamp") or not data.has_key("history"):
        create_user_data(get_current_user_name())
    recent_history = data["history"][-search_length:]
    # print recent_history
    if tool_used in recent_history or "Use <{}>".format(tool_used) in recent_history:
        # print "is recently recored"
        return True
    return False


@try_catch_error
def open_revit_successful():

    tool_used = "Open Revit"
    if is_recently_recorded(tool_used, search_length=2):
        return
    coin_change = 99
    update_account(coins_added=coin_change, history_added=tool_used)
    log_money_change_toast(title="Welcome back!".format(get_current_money(
    )), message="...And here is your daily rewarded of {} EA Coins".format(coin_change), gain_money=True)

    lines = ["How are you doing today?",
             "Welcome back! {}".format(get_current_user_name()),
             "Look at how many coins you have!",
             "Happy you, happy revit. And happy revit, happy project."]

    SPEAK.random_speak(lines)

    if is_money_negative():
        financial_aids = int(abs(get_current_money()) * 0.2)
        update_account(coins_added=financial_aids,
                       history_added="Bankrupt, receiving financial aid ${}".format(financial_aids))


@try_catch_error
def check_out_playlist():
    tool_used = "Check out playlist"
    if is_recently_recorded(tool_used, search_length=5):
        return

    coin_change = 80
    update_account(coins_added=coin_change, history_added=tool_used)
    log_money_change_toast(title="There are some cool demo videos in those playlist!",
                           message="Here is your rewarded of {} EA Coins.".format(coin_change), gain_money=True)


@try_catch_error
def open_doc_with_warning_count(warning_count, doc):

    if warning_count > 0:
        tool_used = "Open doc with more warning"
        price = 1
    else:
        tool_used = "Open doc with less warning"
        price = 2

    """
    if is_recently_recorded(tool_used, search_length = 2):
        return
    """

    # if increase warning, reduce coins---> always opposite
    coin_change = - int(warning_count * price)

    if abs(coin_change) > 2000 and DATA_FILE.get_revit_ui_setting_data(("checkbox_email_opening_warning_diff", True)):
        SPEAK.speak(
            "hmm.. Something is fishy here. How did you have a change of {} coins? Let me write an email. Hold my beer.".format(coin_change))
        EMAIL.email(receiver_email_list=["szhang@ennead.com", "{}@ennead.com".format(get_current_user_name())],
                              subject="EnneadTab Auto Email: Too Many Coins change!",
                              body="Q: Why am I getting this email?\nA: The coins ware rewarded/deducted based on the relative warnings changes since your previous record. It is NOT based on the absolute warning counts. The mini bank feels there might be something fishy about this project file's recent action becasue the coin changes is exceeding $2000. Talk with the bank representative(Sen Z.) to see if everything is alright and he can continue the coins transaction to your account.\nRemember, it might not be you, maybe just something your team did, so don't feel bad talking about it!\n\nUser: {}\nProject File: {}\nWarning Change Since Last Record:{}\nUnit Price:{}\nCoin Change:{}".format(get_current_user_name(),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           get_central_name(
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               doc),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           warning_count,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           price,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           coin_change))
        return
    else:
        update_account(coins_added=coin_change,
                       history_added=tool_used, doc=doc)

    return
    # dont show warnning at begining

    if warning_count > 0:

        log_money_change_toast(title="New Revit warnings will cost you {} EA Coins".format(abs(coin_change)),
                               message="Every new warning will cost you {} coins.".format(
                                   price),
                               gain_money=False)

        lines = ["Warnings, warning, they are everywhere...",
                 "When is the last time you cleaned your revit warning? Two olympics ago?",
                 "There is no shame in getting more warning than before, I repeat, no shame, shame , shame, shame. Did you hear echo?",
                 "Knock knock. Who is there? {} warnings".format(
                     warning_count),
                 "{} warnings walks into a bar...".format(warning_count)]
        EA_UTILITY.random_speak(lines)

    else:

        log_money_change_toast(title="Here is your {} EA Coins reward.".format(abs(coin_change)),
                               message="Rewarded {} coins per warning reduced.".format(
                                   price),
                               gain_money=True)

        lines = ["A clean revit is a happy revit.",
                 "It is always nice to see less warning.",
                 "Let's go! Keep the warning down!"]
        EA_UTILITY.random_speak(lines)


@try_catch_error
def sync_queue_wait_in_line():
    coin_change = 50
    update_account(coins_added=coin_change,
                   history_added="Wait in the sync queue")
    log_money_change_toast(title="Thank you for wait in line!",
                           message="You are rewarded with {} EA Coins.".format(coin_change), gain_money=True)

    lines = ["Waiting in line makes everyone happy.",
             "Please hold while we transfer you to the nearest representative in north pole...",
             "Get some coffee, take a walk. That is good for your health.",
             "You can keep on working on your locals and come back later. "]

    SPEAK.random_speak(lines)


@try_catch_error
def sync_queue_cut_in_line(position_jumped):
    unit_price = 100
    coin_change = - unit_price * int(position_jumped)
    update_account(coins_added=coin_change, history_added="Cut the sync queue")
    log_money_change_toast(title="BOOOO! Cutting Line!", message="Cost you $ {}/person-skipped. Pay {} EA Coins.".format(
        unit_price, abs(coin_change)), gain_money=False)

    lines = ["Line cutter?! Everyone look! Here is a line cutter.",
             "How dare you?!",
             "I am telling somebody, oh you bet, I am telling somebody. I saw the whole thing!"]

    SPEAK.random_speak(lines)


@try_catch_error
def session_too_long():
    tool_used = "Session too long"
    if is_recently_recorded(tool_used, search_length=5):
        return

    coin_change = -300
    update_account(coins_added=coin_change, history_added=tool_used)
    log_money_change_toast(title="Not good to leave Revit open overnight...",
                           message="Penalty...pay {} EA Coins.".format(abs(coin_change)), gain_money=False)
    SPEAK.speak(
        "Your pour Revit has been open for more than 24 hours, give it a rest!")


@try_catch_error
def use_enneadtab(coin_change=20, tool_used="EnneadTab", show_toast=False, search_length=5):

    if is_recently_recorded(tool_used):
        return

    update_account(coins_added=coin_change,
                   history_added="Use <{}>".format(tool_used))

    if not show_toast:
        return
    log_money_change_toast(title="Thanks for using <{}>!".format(
        tool_used), message="Here is your {} EA Coins Reward.".format(coin_change), gain_money=True)


@try_catch_error
def sync_gap_too_long(mins_exceeded, doc_name=None):
    unit_price = 2
    coin_change = - unit_price * int(mins_exceeded)

    history = "Wait too long to Sync."
    if abs(coin_change) > 1000:
        if doc_name:
            additional_note = "\nDocument Name: {}".format(doc_name)
        else:
            additional_note = ""

        no_email_list = ["achi"]
        # if  get_current_user_name() not in no_email_list or
        if DATA_FILE.get_revit_ui_setting_data(("checkbox_email_sync_gap", True)):
            EMAIL.email(receiver_email_list=["szhang@ennead.com", "{}@ennead.com".format(get_current_user_name())],
                                  subject="EnneadTab Auto Email: Sync Gap Way Too Long!",
                                  body_image_link_list=[
                                      r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\lib\EnneadTab\images\revit_wait_too_long.jpg"],
                                  body="Q: Why am I getting this email?\nA: The longer you wait to synchronize file, the higher risk you are at losing work should anything happen to it. \n\nQ: But I dont want to sync often becasue it takes a long time to sync!\nA: I will cap your lost to $1000 even though the record shown you will lose ${}.\n\nQ: That is not fair!\nA: You can also just save your file to reset the timer. And in the rare case that you are detaching file or SaveAs new file, a new record will be generated due to the new file name, so it will seems like the old record never close. If that apply to you, talk to Sen.Z and get refund.\n\nUser: {}{}\nMinutes past since 90 mins mark:{}\nUnit Price:{}\nCoin Change:{}".format(coin_change,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     get_current_user_name(),
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     additional_note,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     mins_exceeded,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     unit_price,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     coin_change))
        # body_image_link_list = [r"L:\4b_Applied Computing\01_Revit\04_Tools\08_EA Extensions\Published\ENNEAD.extension\lib\EnneadTab\images\revit_wait_too_long.jpg"],
        coin_change = -1000
        history = "Wait really really long to Sync. {} mins pass 90 mins mark.".format(
            mins_exceeded)

    update_account(coins_added=coin_change, history_added=history)
    log_money_change_toast(title="Wait too long to sync..",
                           message="Cost you $ {}/minute exceeding suggestion. Pay {} EA Coins.".format(unit_price, abs(coin_change)), gain_money=False)

    lines = ["My pet spider get two new web since you sync last time, they are beautiful.",
             "The longer you wait till synchronize, the more dangerous to lose work.",
             "It sucks to wait for sync, but trust me, it feels worse to lose work becasue you didn't synchronize often enough."]

    SPEAK.random_speak(lines)



@try_catch_error
def warn_revit_session_too_long(non_interuptive = True):
    
    from pyrevit.coreutils import envvars


    if TIME.time_has_passed_too_long(envvars.get_pyrevit_env_var("APP_UPTIME"), tolerence = 60 * 60 * 24):
        #REVIT_FORMS.dialogue(main_text = "This Revit session has been running for more than 24Hours.\n\nPlease consider restarting Revit to release memory and improve performance.")
        session_too_long()
        if non_interuptive:
            NOTIFICATION.messenger(main_text = "Your Revit seesion has been running for more than 24Hours.")
        else:
            REVIT_FORMS.notification(main_text = "This Revit session has been running for more than 24Hours.\nPaying $300 EA Coins.", 
                                     sub_text = "Please consider restarting Revit to release memory and improve performance.", 
                                     window_width = 500, window_height = 300, 
                                     self_destruct = 10)
