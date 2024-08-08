#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Sen Zhang has not writed documentation for this tool, but he should!"
__title__ = "test_coloner"

# from pyrevit import forms #
from pyrevit import script #

import ENNEAD_LOG
from EnneadTab import ERROR_HANDLE
from EnneadTab.REVIT import REVIT_APPLICATION
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
# uidoc = EnneadTab.REVIT.REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()
import traceback
import clr
import os
import System

from EnneadTab import ENVIRONMENT_CONSTANTS
LIBGIT_DLL = "{}\LibGit2Sharp.dll".format(ENVIRONMENT_CONSTANTS.DEPENDENCY_FOLDER_LEGACY)
print (os.path.exists(LIBGIT_DLL))
clr.AddReferenceToFileAndPath(LIBGIT_DLL)

import LibGit2Sharp as libgit
from LibGit2Sharp import Repository, CloneOptions


@ERROR_HANDLE.try_catch_error
def test_coloner():


    # repo_url = "https://github.com/zsenarchitect/EA_Dist.git"
    # clone_dir = r"C:\Users\szhang\Documents\EnneadTab Ecosystem\DIST"
    # print (clone_dir)
    # if not os.path.exists(clone_dir):
    #     os.makedirs(clone_dir)

    # clone_dir = System.String(clone_dir)
    # clone_ops = libgit.CloneOptions()

    # try:
    #     libgit.Repository.Clone(repo_url,clone_dir,clone_ops)
    # except:
    #     print (traceback.format_exc())


            
    import urllib2
    import os
    import zipfile

    def download_and_extract(repo_url, output_dir):
        # Ensure the directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Temp file path
        temp_zip = os.path.join(output_dir, 'repo.zip')

        # Download the zip file
        try:
            request = urllib2.Request(repo_url)
            response = urllib2.urlopen(request)
            data = response.read()  # Read all data from response before closing
            with open(temp_zip, 'wb') as f:
                f.write(data)
            response.close()  # Ensure the response is closed after the data is read
            print("Downloaded the repository zip to {}".format(temp_zip))

            # Extract the zip file
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            print("Extracted the repository to {}".format(output_dir))

            # Clean up the downloaded zip file
            os.remove(temp_zip)

        except Exception as e:
            print("An error occurred: {}".format(e))

    # GitHub repository zip download URL
    repo_url = "https://github.com/zsenarchitect/EA_Dist/archive/refs/heads/master.zip"
    clone_dir = r"C:\Users\szhang\Documents\EnneadTab Ecosystem\DIST"

    download_and_extract(repo_url, clone_dir)




################## main code below #####################


if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    test_coloner()
    ENNEAD_LOG.use_enneadtab(coin_change = 20, tool_used = __title__.replace("\n", " "), show_toast = True)







