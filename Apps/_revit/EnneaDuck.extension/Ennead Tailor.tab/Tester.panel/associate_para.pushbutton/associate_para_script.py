#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "Associate Parameter To Family"
import os
import re

import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from EnneadTab import ERROR_HANDLE, LOG, NOTIFICATION
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_FAMILY
from Autodesk.Revit import DB # pyright: ignore 

from pyrevit import forms
# UIDOC = REVIT_APPLICATION.get_uidoc()
DOC = REVIT_APPLICATION.get_doc()
APP = REVIT_APPLICATION.get_app()


@ERROR_HANDLE.try_catch_error()
def process_family(family_path, built_in_para_name, family_param_name, subc_exclusion):
    # open family path and get family manager
    family_doc = APP.OpenDocumentFile(family_path)
    family_manager = family_doc.FamilyManager


    # get all freeform elements



    # t = DB.Transaction(fam_doc, __title__)
    # t.Start()

    # bind each freeform elements to parameter, assign new subC if needed

    # all error catching is done by the decorator. No need to do try-except inside.
    # t.Commit()


    # load fam_doc to proj_doc
    REVIT_FAMILY.load_family(family_doc, DOC, loading_opt="Placeholder")
    
    # save and close fam_doc
    family_doc.Save()
    family_doc.Close(False)

    # cleanup backup family, use regular expression to match instead of just 0001
    cleanup_backup(family_path)





def cleanup_backup(family_path):


    pattern = re.compile(r'^[a-zA-Z0-9]+?\.\d{4}\.rfa$')
    folder = os.path.dirname(family_path)


    matching_files = [file for file in os.listdir(folder) if pattern.match(file.split('\\')[-1])]
    for file in matching_files:
        os.remove(os.path.join(folder, file))


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def associate_para():


    # pick folder to process,
    folder = forms.pick_folder(title="Pick folder that has your families...")
    if not folder:
        NOTIFICATION.messenger("No folder picked.")
        return


    # gather all family files in folder
    family_paths = [f for f in os.listdir(folder) if f.endswith(".rfa")]
    if len(family_paths) == 0:
        NOTIFICATION.messenger("There is no family in the folder.")
        return


    # pick what built-in-family and family parameter to use, 
    built_in_family_names = [1,2,3]
    selected_built_in_family_para = forms.SelectFromList.show(built_in_family_names,
                                                            button_name = "Pick BuiltInParameter",
                                                            multiselect = False)
    if not selected_built_in_family_para:
        NOTIFICATION.messenger("No BuiltInParameter Picked.")
        return

    
    family_param_name = "Placeholder"
    subc_exclusion = "Placeholder"

    # provide option to return file after long process.
    should_sync_and_close = REVIT_APPLICATION.do_you_want_to_sync_and_close_after_done()

    # loop thru each family
    map(lambda family_path: process_family(family_path, selected_built_in_family_para, family_param_name, subc_exclusion), family_paths)
    
    NOTIFICATION.messenger("All {} families has been updated.".format(len(family_paths)))


    if should_sync_and_close:
        REVIT_APPLICATION.sync_and_close()

################## main code below #####################
if __name__ == "__main__":
    associate_para()







