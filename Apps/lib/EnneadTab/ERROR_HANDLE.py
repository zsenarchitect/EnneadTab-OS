#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback
import os
import EXE
import ENVIRONMENT
import FOLDER
import EMAIL
import USER
import NOTIFICATION

def try_catch_error(func, is_silent=False, is_pass = False):

    def wrapper(*args, **kwargs):

        try:
            out = func(*args, **kwargs)
            return out
        except Exception as e:
            if is_pass:
                return
            print_note(str(e))
            print_note("Wrapper func for EA Log -- Error: " + str(e))
            error = traceback.format_exc()

            subject_line = "EnneadTab Auto Error Log"
            if is_silent:
                subject_line += "(Silent)"
            try:
                EMAIL.email_error(error, func.__name__, USER.get_user_name(
                ), subject_line=subject_line)
            except Exception as e:
                print_note("Cannot send email: {}".format(e))

            if not is_silent:

                error += "\n\n######If you have EnneadTab UI window open, just close the original EnneadTab window(not this textnote). Do no more action, otherwise the program might crash.##########\n#########Not sure what to do? Msg Sen Zhang, you have dicovered a important bug and we need to fix it ASAP!!!!!########"
                error_file = "{}\general_error_log.txt".format(
                    FOLDER.get_EA_dump_folder_file())
                try:
                    with open(error_file, "w") as f:
                        f.write(error)
                except IOError as e:
                    print_note(e)
           
                os.startfile(error_file)

            if ENVIRONMENT.IS_REVIT_ENVIRONMENT and not is_silent:
                NOTIFICATION.messenger(
                    main_text="!Critical Warning, close all Revit UI window from EnneadTab and reach to Sen Zhang.")

    return wrapper


def try_catch_error_silently(func):
    return try_catch_error(func, is_silent=True)

def try_pass(func):
    return try_catch_error(func, is_silent=True, is_pass=True)

def print_note(string):

    if USER.is_enneadtab_developer():
        try:
            from pyrevit import script
            string = str(string)
            script.get_output().print_md(
                "***[DEBUG NOTE]***:{}".format(string))
        except Exception as e:

            print("[DEBUG NOTE]:{}".format(string))
