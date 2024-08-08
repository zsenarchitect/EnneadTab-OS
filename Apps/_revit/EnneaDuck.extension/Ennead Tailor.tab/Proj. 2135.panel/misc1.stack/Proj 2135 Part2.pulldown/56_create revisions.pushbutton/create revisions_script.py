#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Depreciated"
__title__ = "56_Create revisions(Depreciated)"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def create_revision(doc, description, revision_date):
    revision = DB.Revision.Create(doc)
    revision.Description = description
    revision.RevisionDate = revision_date

def main():
    docs = EA_UTILITY.select_top_level_docs()
    if docs is None:
        return

    description = forms.ask_for_string("Revision Name")
    revision_date = forms.ask_for_string("Revision Date")
    for doc in docs:
        t = DB.Transaction(doc, "create revisions")
        t.Start()
        create_revision(doc, description, revision_date)
        t.Commit()

    print("[{}] revision created for the document".format(description))
    for doc in docs:
        print("\n\t\t" + doc.Title)



################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":

    main()


