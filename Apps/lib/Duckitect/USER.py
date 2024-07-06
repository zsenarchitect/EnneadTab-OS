#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

import ENVIRONMENT
import UNIT_TEST 


USER_NAME = os.environ["USERPROFILE"].split("\\")[-1]

# note: why has seperate system key and autodesk keys? becasue some 
# developer might only be handling one software, not both.
Duckitect_DEVELOPERS = {
    "Sen Zhang": {
        "initials": "SZ",
        "system_id": ["szhang", "sen.zhang"],
        "autodesk_id": ["szhangXNLCX"],
        "github_remote": ["zsenarchitect"],
        "email": ["szhang@ennead.com"]
    },
    "Colin Matthews": {
        "initials": "CM",
        "system_id": ["cmatthews", "colin.matthews"],
        "autodesk_id": [],
        "github_remote": ["colinlsmatthews"],
        "email": ["Colin.Matthews@ennead.com"]
    }
}


def get_EA_email_address(user_name = USER_NAME):
    return "{}@ennead.com".format(user_name.replace(".EA",""))



def get_usernames_from_developers():
    """Get all usernames from a dictionary of developers.

    Args:
        username (str): The username or Autodesk ID to check.

    Returns:
        list: Any possible system usernames.
        list: Any possible autodesk usernames.
    """
    
    system_usernames = []
    autodesk_usernames = []
    for key in Duckitect_DEVELOPERS:
        system_usernames += Duckitect_DEVELOPERS[key]["system_id"]
        autodesk_usernames += Duckitect_DEVELOPERS[key]["autodesk_id"]
    return system_usernames, autodesk_usernames


def is_Duckitect_developer():
    """Checks if the current user is a developer of Duckitect.

    Args:
       

    Returns:
        bool: True if the current user is a developer of Duckitect, False if not.
    """
    # declare username variables
    system_usernames, autodesk_usernames = get_usernames_from_developers()

    if ENVIRONMENT.IS_RHINO_ENVIRONMENT:
        return USER_NAME in system_usernames

    if ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return get_autodesk_user_name() in autodesk_usernames


    # in all other terminal conditions:
    return USER_NAME in system_usernames



def get_autodesk_user_name():
    """Get the Autodesk username of the current user.

    Returns:
        str: Autodesk username of the current user.
    """
    if not ENVIRONMENT.IS_REVIT_ENVIRONMENT:
        return None
    import REVIT
    return REVIT.REVIT_APPLICATION.get_app().Username
    
        

IS_DEVELOPER = is_Duckitect_developer()


def get_rhino_developer_emails():
    out = []
    for developer_data in Duckitect_DEVELOPERS.values():
        if len(developer_data["system_id"]) == 0:
            continue
        out += developer_data["email"]
    return out

def get_revit_developer_emails():
    out = []
    for developer_data in Duckitect_DEVELOPERS.values():
        if len(developer_data["autodesk_id"]) == 0:
            continue
        out += developer_data["email"]
    return out


def unit_test():
    import inspect
    import pprint
    # get all the global varibales in the current script
    for i, x in enumerate(sorted(globals())):
        content = globals()[x]
        
        if inspect.ismodule(content):
            
            continue
        if not x.startswith("_") and not callable(content):
            if isinstance(content,dict):
                print(x, " = ")
                pprint.pprint(content)
            else:
                print(x, " = ", content)

    print ("current user [{}] is a developer? {}".format(USER_NAME,
                                                       UNIT_TEST.print_boolean_in_color(is_Duckitect_developer())))
    print ("my system name = {}".format(USER_NAME))
    print ("my autodesk name = {}".format(get_autodesk_user_name()))
    print ("I am  developer? {}".format(UNIT_TEST.print_boolean_in_color(IS_DEVELOPER)))
    
    
    system_usernames, autodesk_usernames = get_usernames_from_developers()
    print ("all system_usernames = {}".format(system_usernames))
    print ("all autodesk_usernames = {}".format(autodesk_usernames))
    print ("all rhino developer emails = {}".format(get_rhino_developer_emails()))
    print ("all revit developer emails = {}".format(get_revit_developer_emails()))
###############
if __name__ == "__main__":
    unit_test()
