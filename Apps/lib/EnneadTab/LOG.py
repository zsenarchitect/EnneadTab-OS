import os
import time
import shutil
import json
import NOTIFICATION
import USER
import DATA_FILE
import ENVIRONMENT
import TIME
import OUTPUT
import FOLDER
import USER




from contextlib import contextmanager

@contextmanager
def log_usage(func,*args):
    t_start = time.time()
    res = func(*args)
    yield res
    t_end = time.time()
    duration = TIME.get_readable_time(t_end - t_start)
    with open(get_log_file(), "a") as f:
        f.writelines('\nRun at {}'.format(TIME.get_formatted_time(t_start)))
        f.writelines('\nDuration: {}'.format(duration))
        f.writelines('\nFunction name: {}'.format(func.__name__))
        f.writelines('\nArguments: {}'.format(args))
        f.writelines('\nResult: {}'.format(res))
    """
    also log here some info on the usage status. Make a context manager
    when:
    who:
    duration:
    file_name:
    error, if any:
    """

# with log_usage(get_log_file()) as f:
#     f.writelines('\nYang is writing!')

    


        
def get_log_folder():
    if ENVIRONMENT.is_Revit_environment():
        log_folder = ENVIRONMENT.REVIT_USER_LOG_FOLDER
    if ENVIRONMENT.is_Rhino_environment():
        log_folder = ENVIRONMENT.RHINO_USER_LOG_FOLDER
    if "log_folder" not in locals():
        log_folder = "{}\LOG".format(FOLDER.get_EA_setting_folder())
        os.makedirs(log_folder, exist_ok = True)
    return log_folder


def get_log_file(user_name = None):
    log_folder = get_log_folder()
    if not user_name:
        user_name = USER.USER_NAME
    return "{}\{}.json".format(log_folder, user_name)

def log(script_path, func_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            log_file = get_log_file()


            if not os.path.exists(log_file):
                with open(log_file, "w") as f:
                    data = dict()
                    data["personal_data"] = {"name": USER.USER_NAME}
                    data["log"] = {}
                    json.dump(data, f)

            with open(log_file, "r") as f:
                data = json.load(f)


            
            t_start = time.time()
            out = func(*args, **kwargs)
            t_end = time.time()
            
            # print (func.__name__)

            data["log"][TIME.get_formatted_current_time()] = {"function_name": func_name,
                                                                "arguments": args,
                                                                "result": out,
                                                                "script_path": script_path,
                                                                "duration": TIME.get_readable_time(t_end - t_start)
                                                                }

            with open(log_file, "w") as f:
                json.dump(data, f)
  
            return out
        return wrapper
    return decorator





def read_log(user_name = USER.USER_NAME):
    log_file = get_log_file(user_name)
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            data = dict()
            json.dump(data, f)
    with open(log_file, "r") as f:
        data = json.load(f)


    print ("Printing user log from <{}>".format(user_name))
    import pprint
    pprint.pprint(data, indent= 4)




class TimeSheet:
    timesheet_data_file = "TIMESHEET.json"
    backup_folder = FOLDER.get_EA_dump_folder_file("timesheet_backup")

    @staticmethod
    def update_timesheet(doc_name):
        if ENVIRONMENT.is_Revit_environment():
            TimeSheet._update_time_sheet_by_software(doc_name, "revit")
        elif ENVIRONMENT.is_Rhino_environment():
            TimeSheet._update_time_sheet_by_software(doc_name, "rhino")
        else:
            TimeSheet._update_time_sheet_by_software(doc_name, "terminal")

    @staticmethod
    def print_timesheet_detail():
        def print_in_style(text):
            if ENVIRONMENT.is_Revit_environment():
                from pyrevit import script
                output = script.get_output()
                lines = text.split("\n")
                for line in lines:
                    output.print_md(line)
                return
            print(text)

        output = ""
        data = DATA_FILE.get_data(TimeSheet.timesheet_data_file) 

        for software in ["revit", "rhino", "terminal"]:
            output += "\n\n"
            output += "\n# Printing time sheet for {}".format(software.capitalize())
            log_data = data.get(software, {})
            for date, doc_data in sorted(log_data.items()):
                output += "\n## Date: {}".format(date)
                for doc_name, doc_info in doc_data.items():
                    output += "\n### Doc Name: {}".format(doc_name)
                    starting_time = doc_info.get("starting_time", None)
                    end_time = doc_info.get("end_time", None)
                    duration = end_time - starting_time if starting_time and end_time else 0
                    if duration < 2:
                        output += "\n    - Open Time: {}".format(TIME.get_formatted_time(starting_time))
                    else:
                        if starting_time and end_time:
                            output += "\n    - Starting Time: {}".format(TIME.get_formatted_time(starting_time))
                            output += "\n    - End Time: {}".format(TIME.get_formatted_time(end_time))
                            output += "\n    - Duration: {}".format(TIME.get_readable_time(duration))
                output += "\n"

        output += "\n\n\nOutput finish!\nIf you are not seeing the record as wished for Rhino files, please 'GetLatest' from menu and follow instruction on Email."

        if ENVIRONMENT.is_Revit_environment():
            TimeSheet.print_revit_log_as_table()
        print_in_style(output)

        if ENVIRONMENT.is_Revit_environment():
            OUTPUT.display_pyrevit_output_on_browser()
        if ENVIRONMENT.is_Rhino_environment():
            import rhinoscriptsyntax as rs
            rs.TextOut(output)

    @staticmethod
    def print_revit_log_as_table(self):
        data = DATA_FILE.get_data(TimeSheet.timesheet_data_file) 
        log_data = data.get("revit", {})
        from pyrevit import script
        output = script.get_output()
        output.insert_divider()
        output.print_md("# This is an alternative display of the Revit Timesheet")

        def print_table(dates):
            table_data = []
            valiad_dates = set()
            proj_dict = dict()
            for date in dates:
                doc_data = log_data.get(date, {})
                valiad_dates.add(date)
                for doc_name, doc_info in doc_data.items():
                    temp = proj_dict.get(doc_name, {})
                    starting_time = doc_info.get("starting_time", None)
                    end_time = doc_info.get("end_time", None)
                    if starting_time and end_time:
                        duration = end_time - starting_time
                        temp[date] = duration
                        proj_dict[doc_name] = temp

            for proj_name, proj_info in sorted(proj_dict.items()):
                total_duration = sum(proj_info.values())
                table_data.append([proj_name] + [TIME.get_readable_time(proj_info.get(date, 0)) if proj_info.get(date, 0) != 0 else "N/A" for date in sorted(valiad_dates)] + [TIME.get_readable_time(total_duration)])

            output.print_table(table_data=table_data,
                               title="Revit Timesheet",
                               columns=["Proj. Name"] + sorted(valiad_dates) + ["Total Hour"])

        all_dates = sorted(log_data.keys())
        seg_max = 10
        for i in range(0, len(all_dates), seg_max):
            if i + seg_max < len(all_dates):
                dates = all_dates[i:i + seg_max]
            else:
                dates = all_dates[i:]
            print_table(dates)

    @staticmethod
    def backup_timesheet(self):


        latest_backup_date = None
        for filename in os.listdir(TimeSheet.backup_folder):
            if filename.endswith(".json"):
                backup_date_str = filename.split("_")[0]
                backup_date = time.strptime(backup_date_str, "%Y-%m-%d")
                if not latest_backup_date or backup_date > latest_backup_date:
                    latest_backup_date = backup_date

        today = time.strftime("%Y-%m-%d")
        if not latest_backup_date or (time.mktime(time.strptime(today, "%Y-%m-%d")) - time.mktime(latest_backup_date)) > 86400:
            backup_file_path = os.path.join(TimeSheet.backup_folder, "{}_{}".format(today, TimeSheet.timesheet_data_file))
            shutil.copy(FOLDER.get_EA_dump_folder_file(TimeSheet.timesheet_data_file), backup_file_path)

    @staticmethod
    def _update_time_sheet_by_software(doc_name, software):
        with DATA_FILE.update_data(TimeSheet.timesheet_data_file) as data:

            software_data = data.get(software, {})
            today = time.strftime("%Y-%m-%d")
            today_data = software_data.get(today, {})
            current_doc_data = today_data.get(doc_name, {})
            if "starting_time" not in current_doc_data:
                current_doc_data["starting_time"] = time.time()
            current_doc_data.update({"end_time": time.time()})
            today_data[doc_name] = current_doc_data
            software_data[today] = today_data
       


    
def unit_test():
    TimeSheet.update_timesheet("test_project_revit_1")
    TimeSheet.update_timesheet("test_project_revit_2")
    TimeSheet.update_timesheet("test_project_rhino_1")
    TimeSheet.print_timesheet_detail()

    # read_log()
    

    
    
###########################################################
if __name__ == "__main__":
    unit_test()