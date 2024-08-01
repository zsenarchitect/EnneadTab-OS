
import time
import EXE
import DATA_FILE
import IMAGE
import EXE
import DATA_FILE
import USER
import ENVIRONMENT
import TIME
import SPEAK

if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
    from REVIT import REVIT_APPLICATION



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

    data = {}
    data["receiver_email_list"] = receiver_email_list
    data["subject"] = subject
    data["body"] = body
    data["body_folder_link_list"] = body_folder_link_list
    data["body_image_link_list"] = body_image_link_list
    data["attachment_list"] = attachment_list
    data["logo_image_path"] = IMAGE.get_image_path_by_name("logo_ennead-e.png")
    DATA_FILE.set_data(data, "email_data.sexyDuck")


    EXE.try_open_app("Emailer")
    SPEAK.speak("enni-ed tab email is sent out. Subject line: {}".format(
        subject.lower().replace("ennead", "enni-ed ")))
    

def email_error(traceback, tool_name, error_from_user, subject_line="EnneadTab Auto Email Error Log"):

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    try:
        if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
            app_uptime = TIME.get_revit_uptime()
            import REVIT
            
            app = REVIT_APPLICATION.get_app()
            
            
            try:
                doc_name = app.ActiveUIDocument.Document.Title
            except:
                try:
                    doc_name = REVIT_APPLICATION.get_doc().Title
                except:
                    doc_name = "N/A"
                
            additional_note = "Version Build: {}\nVersion Number: {}\nVersion Name: {}\nDoc name:{}\n\nRevit UpTime: {}".format(app.VersionBuild,
                                                                                                                                app.VersionNumber,
                                                                                                                                app.VersionName,
                                                                                                                                doc_name,
                                                                                                                                app_uptime)
        elif ENVIRONMENT.IS_RHINO_ENVIRONMENT:
            import rhinoscriptsyntax as rs
            import scriptcontext as sc
            additional_note = "File in trouble:{}\nCommand history before disaster:\n{}".format(sc.doc.Path or None,
                                                                                rs.CommandHistory())

            
        else:
            additional_note = ""
    except Exception as e:
        print(e)
        additional_note = str(e)
    body = "{}\nError happens on {}'s machine when running {}.\n\nDetail below:\n{}\n\n{}".format(t, 
                                                                                             error_from_user, 
                                                                                             tool_name, 
                                                                                             traceback,
                                                                                             additional_note)

    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        developer_emails = USER.get_revit_developer_emails()
        if "h" in app_uptime and 50 < int(app_uptime.split("h")[0]):
            email_to_self(subject="I am tired...Revit running non-stop for {}".format(app_uptime),
                          body="Hello,\nI have been running for {}.\nLet me rest and clear cache!\n\nDid you know that restarting your Revit regularly can improve performance?\nBest regard,\nYour poor Revit.". format(app_uptime))
            
    if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
        developer_emails = USER.get_rhino_developer_emails()


    if USER.IS_DEVELOPER:
        developer_emails = [USER.get_EA_email_address()]


    email(receiver_email_list=developer_emails,
          body=body,
          subject=subject_line,
          body_folder_link_list=None,
          body_image_link_list=None,
          attachment_list=None)


def email_to_self(subject="EnneadTab Auto Email to Self",
                body=None,
                body_folder_link_list=None,
                body_image_link_list=None,
                attachment_list=None):
    email(receiver_email_list=[USER.get_EA_email_address()],
          subject=subject,
          body=body,
          body_folder_link_list=body_folder_link_list,
          body_image_link_list=body_image_link_list,
          attachment_list=attachment_list)



def unit_test():
    email_to_self(subject="Test Email for compiler",
                  body="Happy Howdy. This is a quick email test to see if the base communication still working")