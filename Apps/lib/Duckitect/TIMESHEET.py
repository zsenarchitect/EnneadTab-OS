import os
import time
import shutil

import DATA_FILE
import ENVIRONMENT
import TIME
import OUTPUT
import FOLDER
import USER

TIMESHEET_DATA_FILE = "timesheet_{}.json".format(USER.USER_NAME)


@FOLDER.backup_data(TIMESHEET_DATA_FILE , "timesheet")
def update_timesheet(doc_name):
    app_name = ENVIRONMENT.get_app_name()
    _update_time_sheet_by_software(doc_name, app_name)

def print_timesheet_detail():
    def print_in_style(text):
        if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
            from pyrevit import script
            output = script.get_output()
            lines = text.split("\n")
            for line in lines:
                output.print_md(line)
            return
        print(text)

    output = ""
    data = DATA_FILE.get_data(TIMESHEET_DATA_FILE)

    for software in ["revit", "rhino", "terminal"]:
        output += "\n\n"
        output += "\n# Printing timesheet for {}".format(software.capitalize())
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

    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        print_revit_log_as_table()
    print_in_style(output)

    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        OUTPUT.display_output_on_browser()
    if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
        import rhinoscriptsyntax as rs
        rs.TextOut(output)

def print_revit_log_as_table():
    data = DATA_FILE.get_data(TIMESHEET_DATA_FILE)
    log_data = data.get("revit", {})
    from pyrevit import script
    output = script.get_output()
    output.insert_divider()
    output.print_md("# This is an alternative display of the Revit Timesheet")

    def print_table(dates):
        table_data = []
        valid_dates = set()
        proj_dict = dict()
        for date in dates:
            doc_data = log_data.get(date, {})
            valid_dates.add(date)
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
            table_data.append([proj_name] + [TIME.get_readable_time(proj_info.get(date, 0)) if proj_info.get(date, 0) != 0 else "N/A" for date in sorted(valid_dates)] + [TIME.get_readable_time(total_duration)])

        output.print_table(table_data=table_data,
                           title="Revit Timesheet",
                           columns=["Proj. Name"] + sorted(valid_dates) + ["Total Hour"])

    all_dates = sorted(log_data.keys())
    seg_max = 10
    for i in range(0, len(all_dates), seg_max):
        if i + seg_max < len(all_dates):
            dates = all_dates[i:i + seg_max]
        else:
            dates = all_dates[i:]
        print_table(dates)



def _update_time_sheet_by_software(doc_name, software):
    with DATA_FILE.update_data(TIMESHEET_DATA_FILE) as data:
        software_data = data.get(software, {})
        today = time.strftime("%Y-%m-%d")
        
        today_data = software_data.get(today, {})
        current_doc_data = today_data.get(doc_name, {})
        if "starting_time" not in current_doc_data:
            current_doc_data["starting_time"] = time.time()
        current_doc_data.update({"end_time": time.time()})
        today_data[doc_name] = current_doc_data
        
        software_data[today] = today_data
        data[software] = software_data


def unit_test():
    update_timesheet("test_project_revit_1")
    update_timesheet("test_project_revit_2")
    update_timesheet("test_project_rhino_1")

    print_timesheet_detail()


if __name__  == "__main__":
    unit_test()