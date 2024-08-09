#!/usr/bin/python
# -*- coding: utf-8 -*-



__doc__ = "Depreciated"
__title__ = "55_Add field to schedule(Depreciated)"

from pyrevit import forms #
from pyrevit import script #
# from pyrevit import revit #
import EA_UTILITY
import proDUCKtion # pyright: ignore 
proDUCKtion.validify()
from Autodesk.Revit import DB # pyright: ignore 
# from Autodesk.Revit import UI # pyright: ignore
doc = __revit__.ActiveUIDocument.Document # pyright: ignore

def get_schedules():
    all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()

    all_schedules = filter(lambda x: all([str(x.ViewType) == "Schedule", "<Revision" not in x.Name]), all_views)
    all_schedules.sort(key = lambda x:x.Name)
    schedules = forms.SelectFromList.show(all_schedules,
                                            name_attr = "Name",
                                            multiselect = True)

    return schedules

def get_field(sample_schedule):
    all_fileds = sample_schedule.Definition.GetSchedulableFields()
    class MyOption(forms.TemplateListItem):
        @property
        def name(self):
            return self.item.GetName(doc)

    all_fileds = [MyOption(x) for x in all_fileds]
    all_fileds.sort(key = lambda x: x.name)
    filed = forms.SelectFromList.show(all_fileds,
                                    name_attr = "Name",
                                    multiselect = False)
    return filed

def main():
    schedules = get_schedules()
    if schedules is None:
        return

    field = get_field(schedules[0])
    map(lambda x:add_filed_to_schedule(field, x), schedules)
    #definition = EA_UTILITY.pick_shared_para_definition(doc)
    print("[{}] field added to schedules:".format(field.GetName(doc)))
    for schedule in schedules:
        print("\n\t\t{}".format(schedule.Name))

def add_filed_to_schedule(field, schedule):
    schedule.Definition.AddField(field)

################## main code below #####################
output = script.get_output()
output.close_others()


if __name__ == "__main__":
    t = DB.Transaction(doc, "add field to schedule")
    t.Start()
    main()
    t.Commit()


