__doc__ = """Which Legand and Schedule were used? Where are they?
If you have been wondering about those question, this tool can help you with it.

It list all the current locations for the schedules and legend, with a clickable link!"""
__title__ = "Legend&Schedule\nWhere?"
__tip__ = True

from pyrevit import script
from Autodesk.Revit import DB # pyright: ignore

from EnneadTab.REVIT import REVIT_APPLICATION
from EnneadTab import ERROR_HANDLE
uidoc = REVIT_APPLICATION.get_uidoc()
doc = REVIT_APPLICATION.get_doc()

class Solution:
    def who_created(self, view_name):
        view = filter(lambda x: x.Name == view_name, self.all_views)[0]
        view_history = DB.WorksharingUtils.GetWorksharingTooltipInfo(doc, view.Id)
        return view_history.Creator

    @staticmethod
    def Diff(li1, li2):
        return list(set(li1) - set(li2)) + list(set(li2) - set(li1))


    def update_dict(self,name,item):
        if name in self.dicts.keys():
            self.dicts[name].append(item)
        else:
            self.dicts[name] = [item]
            
            
    @ERROR_HANDLE.try_catch_error()
    def main(self):
        onsheet_schedule_names = set()
        on_sheet_schedules = DB.FilteredElementCollector(doc).OfClass(DB.ScheduleSheetInstance).WhereElementIsNotElementType().ToElements()
        for schedule in on_sheet_schedules:
            master_schedule = doc.GetElement(schedule.ScheduleId)
            if "<Revision Schedule>" in master_schedule.Name:
                continue

            sheet = doc.GetElement(schedule.OwnerViewId)
            print ("'{}' schedule on sheet: '{}-{}' ".format(master_schedule.Name, output.linkify(sheet.Id, title = "{}".format(sheet.SheetNumber)), sheet.Name))
            onsheet_schedule_names.add(master_schedule.Name)

        print ("\n\n\n######################\n\n")


        self.dicts = {}
        sheets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheet).WhereElementIsNotElementType().ToElements()
        for sheet in sheets:
            view_ids = sheet.GetAllPlacedViews()
            views = [doc.GetElement(x) for x in view_ids]
            for view in views:
                if view.ViewType == DB.ViewType.Legend:
                    self.update_dict(view.Name, sheet.Id)

        for key in self.dicts.keys():
            print ("Legend '{}' in sheet:".format(key))
            #print self.dicts[key]
            for sheet_id in self.dicts[key]:
                sheet = doc.GetElement(sheet_id)
                print ("\t'{}-{}' ".format(output.linkify(sheet.Id, title = "{}".format(sheet.SheetNumber)), sheet.Name))

        print ("\n\n\n######################\n\n")
        self.all_views = DB.FilteredElementCollector(doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
        legends = filter(lambda x: x.ViewType == DB.ViewType.Legend, self.all_views)
        legend_names = map(lambda x: x.Name, legends)

        nosheet_legend = Solution.Diff(legend_names , self.dicts.keys())
        nosheet_legend.sort(key = lambda x: x, reverse = False)
        if len(nosheet_legend) > 0:
            print ("\n\nThe following legends are not showing anywhere on sheet.")
            for x in  nosheet_legend:
                print ("\t\t{}   (created by:{})".format(x,self.who_created(x)))

        all_schedules = filter(lambda x: x.ViewType == DB.ViewType.Schedule, self.all_views)
        all_schedule_names = set()
        for schedule in all_schedules:
            if "<Revision Schedule>"  in schedule.Name:
                continue
            all_schedule_names.add(schedule.Name)

        nosheet_schedule_name = list(all_schedule_names.difference(onsheet_schedule_names))
        nosheet_schedule_name.sort(key = lambda x: x, reverse = False)
        if len(nosheet_schedule_name) > 0:
            print ("\n\nThe following schedule are not showing anywhere on sheet.")
            for x in  nosheet_schedule_name:
                print( "\t\t{}   (created by:{})".format(x,self.who_created(x)))

        
################## main code below #####################

if __name__ == "__main__":
    output = script.get_output()
    output.close_others()
    Solution().main()
    
