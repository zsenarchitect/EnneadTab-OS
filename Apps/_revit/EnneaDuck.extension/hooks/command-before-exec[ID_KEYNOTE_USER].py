
from pyrevit import  EXEC_PARAMS

from EnneadTab import ERROR_HANDLE, NOTIFICATION
args = EXEC_PARAMS.event_args
doc = args.ActiveDocument 



@ERROR_HANDLE.try_catch_error(is_silent=True)
def main():

    # if doc.IsFamilyDocument:
    #     return
    
    # if EnneadTab.USER.get_user_name() == "yumeng.an" and EnneadTab.TIME.get_YYYYMMDD() == "231215":
    #     return
    # if EnneadTab.USER.get_user_name() == "hjlee" and EnneadTab.TIME.get_YYYYMMDD() < "240315":
        
    #     return
    NOTIFICATION.duck_pop(main_text = "EnneaDuck dislikes [UserKeynote], that tag will not link to other database! Quack!\nOnly use [UserKeynote] when you have ABSOLUTELY no choice.")
    print("this duck is enforced and will not be turned off by setting.")
    args.Cancel = False

                                        
############################

if __name__ == '__main__':
    main()