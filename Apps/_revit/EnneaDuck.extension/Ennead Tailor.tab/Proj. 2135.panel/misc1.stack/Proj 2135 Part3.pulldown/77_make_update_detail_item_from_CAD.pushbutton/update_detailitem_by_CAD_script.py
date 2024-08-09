#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "For each selected dwg file, create new detail item family and load in the dwg, save family as the same name as the dwg, then load the family to project.\n\nThis batch process is handy when your consaltant gives you dozens of CAD drawing and you need to convert all of them to detail item family.\n\nYou should also checkout EnneadTab for CAD for some CAD batch processing related tto this workflow."
__title__ = "77_Create/Update detail item from CAD"
__youtube__ = "https://youtu.be/fv0UqOl_mAI"
import clr
from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
import os.path as op
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore
app = doc.Application




class FamilyOption(DB.IFamilyLoadOptions):
    def OnFamilyFound(self, familyInUse, overwriteParameterValues):
        #update_log( "#Normal Family Load option")
        #update_log( "is family in use?: {}".format(familyInUse))
        overwriteParameterValues = True# true means use project value
        #update_log( "is overwriteParameterValues?: {}".format(overwriteParameterValues))
        #update_log( "should load")
        return True

    def OnSharedFamilyFound(self, sharedFamily, familyInUse, source, overwriteParameterValues):
        #update_log( "#Shared Family Load option")
        #update_log( "is family in use?: {}".format(familyInUse))
        overwriteParameterValues = True
        #update_log( "is overwriteParameterValues?: {}".format(overwriteParameterValues))


        source = DB.FamilySource.Family
        #source = DB.FamilySource.Family
        #update_log( "is shared component using family or project definition?: {}".format(str(source)))
        #update_log( "should load")
        return True


def make_update_detail_item_from_CAD():
    if doc.IsFamilyDocument:
        EA_UTILITY.dialogue(main_text = "Should do this from a project document not a family document.")
        return



    source_files = forms.pick_file(file_ext = "dwg", multi_file = True)
    opts = ["Always Override", "Let me decide one by one"]
    res = EA_UTILITY.dialogue(main_text = "If encountering existing family, how should it handle?", options = opts)
    is_always_override = True
    if res == opts[1]:
        is_always_override = False
    map(lambda x: process_cad(x, is_always_override), source_files)

def process_cad(source_file, is_always_override) :
    #print source_file
    content_name = source_file.split('\\')[-1].split(".")[0]
    #print content_name

    family_template_path = r"L:\4b_Applied Computing\01_Revit\02_Template\02_Asia\EA_Family Templates\Metric_Detail Component.rft"
    family_doc = app.NewFamilyDocument (family_template_path)

    family_path = source_file.replace(".dwg", ".rfa")


    if op.isfile(family_path) :
        if not is_always_override:
            opts = ["Override", "Skip loading"]
            res = EA_UTILITY.dialogue(main_text = "Family <{}> existing, Do you want to override?".format(content_name), options = opts)
            if res == opts[1]:
                return
        save_as_option = DB.SaveAsOptions()
        save_as_option.OverwriteExistingFile = True
        try:
            family_doc.SaveAs(family_path, save_as_option)
        except Exception as e:
            EA_UTILITY.dialogue(main_text = str(e), sub_text = "Family: {}".format(content_name))
            return
    else:
        family_doc.SaveAs(family_path)

    EA_UTILITY.open_and_active_project(family_path)
    t = DB.Transaction(family_doc, "import DWG")
    t.Start()
    options = DB.DWGImportOptions()
    cad_import_id = clr.StrongBox[DB.ElementId]()
    family_doc.Import(source_file, options, family_doc.ActiveView, cad_import_id)


    family_manager = family_doc.FamilyManager
    family_manager.NewType("DD")
    t.Commit()
    family_doc.Save()
    family_doc.LoadFamily(get_project_doc(),FamilyOption())

    #family_path = "{}\\{}.rft".format(source_file.split(content_name)[0], content_name)
    EnneadTab.REVIT.REVIT_FORMS.notification(main_text = "Family <{}> loaded/updated, now go back to the project <{}> to insert the detail item family".format(content_name, doc.Title), self_destruct = 3)
    pass


def get_project_doc():
    for open_doc in EA_UTILITY.get_top_revit_docs():
        if not open_doc.IsFamilyDocument:
            if open_doc.Title == doc.Title:
                return open_doc

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    make_update_detail_item_from_CAD()
