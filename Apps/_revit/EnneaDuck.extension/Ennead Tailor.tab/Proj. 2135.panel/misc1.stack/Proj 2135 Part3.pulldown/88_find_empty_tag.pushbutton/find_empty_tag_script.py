#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Find keynote tags that is current empty."
__title__ = "88_find_empty_tag"

# from pyrevit import forms #
from pyrevit import script #

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def find_empty_tag():
    pass
    key_note_tags = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_KeynoteTags).WhereElementIsNotElementType().ToElements()


    #T = DB.TransactionGroup(doc, "refressh tag display")
    #T.Start()
    for tag in key_note_tags:

        key_number = tag.Parameter[DB.BuiltInParameter.KEY_VALUE].AsString()
        #key_number = tag.Parameter[DB.BuiltInParameter.KEYNOTE_NUMBER].AsString()
        if key_number == "":

            view = doc.GetElement(tag.OwnerViewId)
            print("\n\n{} has empty key number in view <{}>.".format(output.linkify(tag.Id, title = "Keynote Tag"), view.Name))
            t = DB.Transaction(doc, "step1")
            t.Start()
            tag.Pinned = not tag.Pinned
            tag.HasLeader = not tag.HasLeader
            doc.Regenerate()
            t.Commit()


            t = DB.Transaction(doc, "step2")
            t.Start()
            tag.Pinned = not tag.Pinned
            tag.HasLeader = not tag.HasLeader
            doc.Regenerate()
            t.Commit()

            key_number = tag.Parameter[DB.BuiltInParameter.KEY_VALUE].AsString()
            if key_number == "":
                print("Fix failed.")
            else:
                print("It has now been fixed.")

            #key_number = tag.Parameter[DB.BuiltInParameter.KEY_VALUE].AsString()
            #print "after alter, curent key_number = " + key_number
            # pin unpin will update
            # if has not leader, turn on leader and turn off, also update



    #T.Commit()
    print("tool finished")
    """

    import selected object style from project or family
    """
################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    find_empty_tag()
