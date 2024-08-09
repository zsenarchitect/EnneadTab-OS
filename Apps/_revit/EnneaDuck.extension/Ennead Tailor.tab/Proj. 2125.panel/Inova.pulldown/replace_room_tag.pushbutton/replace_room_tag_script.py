#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Replacing one type of roomtag on many sheets to another type.\n\nThis process is not the same as merging. It is just doing selected replacement."
__title__ = "2124_Replace Room Tag"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()

from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore



def pick_type(title_note):
    families = DB.FilteredElementCollector(doc).OfClass(DB.Family).WhereElementIsNotElementType().ToElements()
    families = sorted(families, key = lambda x: x.Name)
    family = forms.SelectFromList.show(families,
                                        multiselect = False,
                                        name_attr = 'Name',
                                        title = "Pick family" + title_note,
                                        button_name = 'Select Family')
    if not family:
        return


    types = [doc.GetElement(x) for x in family.GetFamilySymbolIds ()]
    types = sorted(types, key = lambda x: x.LookupParameter("Type Name").AsString())
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return "[{}]: {}".format(self.FamilyName, self.LookupParameter("Type Name").AsString())
    types = [MyOption(x) for x in types]
    family_type = forms.SelectFromList.show(types,
                                            multiselect = False,
                                            title = "Pick family type" + title_note,
                                            button_name = 'Select Type')
    if not family_type:
        return

    print (family_type)
    return family_type

   

def replace_room_tag():
    sheets = forms.select_sheets()

    if not sheets:
        return

    bad_tag_type = pick_type(" of bad tag")
    if not bad_tag_type:
        return
    good_tag_type = pick_type(" of target tag")
    if not good_tag_type:
        return

    #print "bad type = " + str(bad_tag_type)


    t = DB.Transaction(doc, __title__)
    t.Start()
    for i, sheet in enumerate(sheets):
        print("\n\n---{}/{} sheet: {}-{}".format(i + 1, len(sheets), sheet.SheetNumber, sheet.Name))
        for view_id in sheet.GetAllPlacedViews ():
            view = doc.GetElement(view_id)
            tags = DB.FilteredElementCollector(doc, view.Id).OfClass(DB.SpatialElementTag ).WhereElementIsNotElementType().ToElements()
            #print "all tags = {}".format(tags)
            tags = filter(lambda x: hasattr(x, "RoomTagType"), tags )
            #print "all tags with roomtype property = {}".format(tags)
            tags = filter(lambda x: x.RoomTagType.Id == bad_tag_type.Id, tags )
            #print "all tags with bad type = {}".format(tags)
            for tag in tags:
                tag.RoomTagType = good_tag_type
            print ("\t\tChanging {} tags in view: {}".format(len(tags), view.Name))
    t.Commit()


################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    replace_room_tag()
    
