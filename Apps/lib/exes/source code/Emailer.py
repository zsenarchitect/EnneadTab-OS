import traceback
import json

import os
import win32com.client
import io

def send_email():


    file_name = "EA_EMAIL.json"
    dump_folder = "{}\Documents\EnneadTab Settings".format(os.environ["USERPROFILE"])
    file_path = "{}\{}".format(dump_folder, file_name)
    if not os.path.exists(file_path):
        print ("no json")
        return

    
    with io.open(file_path, encoding='utf8') as f:
        data = json.load(f)


    receiver_email_list = data["receiver_email_list"]
    temp = ""
    for email in receiver_email_list:
        temp += "{}; ".format(email)
    receiver_email_list = temp

    subject = data["subject"]
    body = data["body"]
    body_folder_link_list = data["body_folder_link_list"]
    body_image_link_list = data["body_image_link_list"]
    attachment_list = data["attachment_list"]
    schedule_time = data["schedule_time"]


    content = body

    
    # Connect to Outlook and send the email
    outlook = win32com.client.Dispatch("Outlook.Application")
    message = outlook.CreateItem(0)
    message.To = receiver_email_list
    message.Subject = subject
    message.HTMLBody = content

    if body_folder_link_list:
        # insert hyper link to folder in the body of the email
        # folder_link = r"I:\2135\1_Study\test print"

        for link in body_folder_link_list:
            message.HTMLBody += '<br><br><a href="{0}">Click here to access the folder: {0}</a>'.format(link)

    if body_image_link_list:
        # insert image to thge body of the email,
        for link in body_image_link_list:
            message.HTMLBody += '<br><br><img src="{}"><br><br>'.format(link)

    # insert image to thge body of the email, make this the EnneadTab logo
    logo_image_path = data.get("logo_image_path")
    if logo_image_path:
        message.HTMLBody += '<br><br><img src="{}"><br><br>'.format(logo_image_path)

    if attachment_list:
        for file in attachment_list:
            message.Attachments.Add(file, 1)

    if schedule_time:
        import time
        while time.time() < schedule_time:
            time.sleep(60)

    message.Send()
    # print ("finish")
    
    os.remove(file_path)



if __name__ == "__main__":
    try:
        send_email()
    except:

        error = traceback.format_exc()
        error_file = "{}\Documents\EnneadTab Settings\ERROR_LOG_email.txt".format(os.environ["USERPROFILE"])
        with open(error_file, "w") as f:
            f.write(error)



    print ("tool end")
