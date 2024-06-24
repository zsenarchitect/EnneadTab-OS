
import EXE
import DATA_FILE
import IMAGE

def email(receiver_email_list,
          body,
          subject="EnneadTab Auto Email",
          body_folder_link_list=None,
          body_image_link_list=None,
          attachment_list=None):
    """sender email is not required for outlook approch
    """
    if not body:
        print ("Missing body of the email.....")
        return

    if not receiver_email_list:
        print ("missing email receivers....")
        return


    if isinstance(receiver_email_list, str):
        print("Prefer list but ok.")
        receiver_email_list = receiver_email_list.rstrip().split(";")


    body = body.replace("\n", "<br>")


    with DATA_FILE.update_data("EA_EMAIL.json") as data:
        data["receiver_email_list"] = receiver_email_list
        data["subject"] = subject
        data["body"] = body
        data["body_folder_link_list"] = body_folder_link_list
        data["body_image_link_list"] = body_image_link_list
        data["attachment_list"] = attachment_list
        data["logo_image_path"] = IMAGE.get_image_path_by_name("EnneadTab_Logo.png")


    EXE.try_open_app("EA_EMAIL")

