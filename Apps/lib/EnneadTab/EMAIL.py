



def email(sender_email=None,
          receiver_email_list=None,
          subject="EnneadTab Auto Email",
          body=None,
          body_folder_link_list=None,
          body_image_link_list=None,
          attachment_list=None,
          schedule_time=None):
    """sender email is not required for outlook approch
    schedule time is the desired time in uni seconds
    """

    if not receiver_email_list:
        return
    if isinstance(receiver_email_list, str):
        print("Prefer list but ok.")
        receiver_email_list = receiver_email_list.rstrip().split(";")

    if not body:
        return

    body = body.replace("\n", "<br>")

    data = dict()
    data["receiver_email_list"] = receiver_email_list
    data["subject"] = subject
    data["body"] = body
    data["body_folder_link_list"] = body_folder_link_list
    data["body_image_link_list"] = body_image_link_list
    data["attachment_list"] = attachment_list
    data["schedule_time"] = schedule_time
    data["logo_image_path"] = r"L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\lib\EnneadTab_Logo.png"

    file_name = "EA_EMAIL.json"
    dump_folder = FOLDER.get_EA_local_dump_folder()
    file_path = "{}\{}".format(dump_folder, file_name)
    DATA_FILE.save_dict_to_json(data, file_path)


    exe_location = "L:\\4b_Applied Computing\\01_Revit\\04_Tools\\08_EA Extensions\\Project Settings\\Exe\\EA_EMAIL\\EA_EMAIL.exe"

    
    EXE.open_file_in_default_application(exe_location)

