__doc__ = "Reset all keynote tag local override color to default. It might got its color from the other checking type button."
__title__ = "KeynoteTAG Reset Color"
__tip__ = True


import proDUCKtion # pyright: ignore 
from EnneadTab.REVIT import REVIT_APPLICATION, REVIT_SELECTION
from EnneadTab import ERROR_HANDLE
from pyrevit import forms, DB, revit, script

uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()


@ERROR_HANDLE.try_catch_error()
def main():
    key_note_tags = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_KeynoteTags).WhereElementIsNotElementType().ToElements()

    processed_element_count = 0
    with revit.Transaction("reset keynote tag"):
        for tag in key_note_tags:
            if REVIT_SELECTION.is_changable(tag):
                print ("---tag being owned, skip reset")
                continue
            view = revit.doc.GetElement(tag.OwnerViewId)
            if REVIT_SELECTION.is_changable(view):
                print ("---view [{}] being owned, skip reset".format(view.Name))
                continue
            OG_setting = DB.OverrideGraphicSettings()
            view.SetElementOverrides(tag.Id, OG_setting)
            processed_element_count += 1

    forms.alert("{} keynotes have been reset to default color.\n{} keynotes skipped due to ownership.\nSee output for details".format(processed_element_count, len(key_note_tags) - processed_element_count))
################## main code below #####################
if __name__ == "__main__":
        
    output = script.get_output()
    output.close_others()
    main()

